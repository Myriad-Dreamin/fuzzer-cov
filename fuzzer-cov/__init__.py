
import platform
import typing
import tempfile
import subprocess
import os
import argparse
from pathlib import Path

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


T = typing.TypeVar('T')
class BuildContainer(Protocol):
    opts: object

    def register_impl(self, t: type, p: type=None):
        raise NotImplementedError

    def resolve(self, t: typing.Type[T]) -> T:
        raise NotImplementedError

class FuzzerExecutor(Protocol):
    def __init__(self, container: BuildContainer):
        raise NotImplementedError
    
    def exec_one_file(self, case_file: str, silent: int=1):
        raise NotImplementedError
    
    def exec_corpus_set(self, corpus_dir: str, silent: int=1):
        raise NotImplementedError


class Logger(Protocol):

    def verbose(self, msg, log_obj=None):
        raise NotImplementedError

    def info(self, msg, log_obj=None):
        raise NotImplementedError

    def warn(self, msg, log_obj=None):
        raise NotImplementedError

    def debug(self, msg, log_obj=None):
        raise NotImplementedError

    def critical(self, msg, log_obj=None):
        raise NotImplementedError

class CommandExecutor(object):
    def __init__(self, container: BuildContainer):
        self.logger = container.resolve(Logger)
    
    def must_exec(self, cmd, silent: int=1):
        code, out = self.exec(cmd, silent)
        if code:
            raise Exception(f"command executor exit with non-zero code: {code}")
        return out
    
    def exec(self, cmd, silent: int=1):

        self.logger.info(f"CMD: {cmd}", { 'cmd': cmd })

        process = subprocess.Popen(cmd, stdin=None,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
        lines = []
        mx = 0
        if silent == 2:
            print("")
        for stdout_line in iter(process.stdout.readline, ""):
            stdout_line = stdout_line.rstrip('\n')
            if silent == 0:
                print(stdout_line)
            elif silent == 2:
                mx = max(mx, len(stdout_line))
                if 'warning' in stdout_line.lower():
                    print((" "*mx)+"\r"+stdout_line)
                else:
                    print((" "*mx)+"\r"+stdout_line, end='')
            lines.append(stdout_line)
        process.stdout.close()
        exit_code = process.wait()
        if silent == 2:
            print("")

        if exit_code:
            self.logger.info(f"    Non-zero exit status '{exit_code}' for CMD: {cmd}", { 'exit_code': exit_code, 'cmd': cmd })
        return exit_code, lines

class LibFuzzerInstanceExecutor(FuzzerExecutor):
    fuzzer_path: str
    logger: Logger

    def __init__(self, container: BuildContainer):
        self.fuzzer_path = container.opts.fuzzer_path
        self.logger = container.resolve(Logger)
        self.cmd_executor = CommandExecutor(container)

    def exec_one_file(self, case_file: str, silent: int=1):
        return self.cmd_executor.exec(f"{self.fuzzer_path} {case_file} -runs=1 -timeout=600", silent)

    def exec_corpus_set(self, corpus_dir: str, silent: int=1):
        return self.cmd_executor.exec(f"{self.fuzzer_path} {corpus_dir} -runs=1 -timeout=600", silent)


class LCovOutputPathPolicy(object):
    def __init__(self, container: BuildContainer):
        self.lcov_output_dir = container.opts.lcov_output_dir
        self.lcov_base_file = os.path.join(self.lcov_output_dir, 'trace.lcov_base')
        self.lcov_info_file = os.path.join(self.lcov_output_dir, 'trace.lcov_info')
        self.lcov_info_final_file = os.path.join(self.lcov_output_dir, 'trace.lcov_info_final')
    
    def initialize_file_structure(self, clean):
        cov_lcov_output_path = Path(self.lcov_output_dir)
        cov_lcov_output_path.mkdir(parents=True, exist_ok=True)

        if os.path.exists(self.lcov_base_file) and clean:
            os.unlink(self.lcov_base_file)
        if os.path.exists(self.lcov_info_file) and clean:
            os.unlink(self.lcov_info_file)
        if os.path.exists(self.lcov_info_final_file) and clean:
            os.unlink(self.lcov_info_final_file)

class GenHtmlOutputPathPolicy(object):

    def __init__(self, container: BuildContainer):
        self.gen_html_output_dir = container.opts.gen_html_output_dir
        self.lcov_info_final_file = ''
    
    def initialize_file_structure(self, clean):
        output_path = Path(self.gen_html_output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    
    def use_lcov_path_policy(self, lcov_path_policy: LCovOutputPathPolicy):
        self.lcov_info_final_file = lcov_path_policy.lcov_info_final_file
        return self

def demangle(symbol):
    return subprocess.check_output(['c++filt', '-n', symbol.strip()]).decode().strip()

def filter_lcov(lines, verbose=False):
    defs, srcfile = {}, ''
    for line in lines:
        if line.startswith('SF:'):
            defs = {}
            srcfile = line[3:].strip()
        elif line.startswith('end_of_record'):
            defs = {}
        elif line.startswith('FN:'):
            lineno, symbol = line[3:].split(',')
            defs[lineno] = demangle(symbol)
        elif line.startswith('DA:'):
            lineno = line[3:].split(',')[0]
            if lineno in defs:
                if verbose:
                    print(f'Ignoring: {srcfile}:{lineno}:{defs[lineno]}')
                continue
        yield line

class LCovRunner(object):
    source_dir: str
    lcov_path: str
    lcov_opts: str
    lcov_exclude_opts: str
    lcov_cmd: str
    lcov_web_path: str

    def __init__(self, container: BuildContainer):
        self.lcov_path = container.opts.lcov_path
        self.source_dir = container.opts.source_dir
        self.lcov_opts = ''
        self.lcov_exclude_opts = ''
        if container.opts.enable_branch_coverage:
            self.lcov_opts += ' --rc lcov_branch_coverage=1'
        if container.opts.lcov_follow_links:
            self.lcov_opts += ' --follow'
        if container.opts.lcov_exclude_pattern:
            self.lcov_exclude_opts = container.opts.lcov_exclude_pattern
        self.cmd_executor = CommandExecutor(container)
        self.lcov_cmd = f"{self.lcov_path} {self.lcov_opts}"
        self.lcov_web_path = os.path.join(container.opts.output_dir, 'web')
        self.lcov_cov_info_path = os.path.join(container.opts.output_dir, 'cov_info')
        os.makedirs(self.lcov_web_path, exist_ok=True)
    
    def init_coverage_files(self, policy: LCovOutputPathPolicy, silent: int=1):
        self.cmd_executor.must_exec(f"{self.lcov_cmd} --no-checksum --zerocounters --directory {self.source_dir}", silent=silent)
        self.cmd_executor.must_exec(f"{self.lcov_cmd} --no-checksum --capture --initial --directory {self.source_dir} --output-file {policy.lcov_base_file}", silent=silent)

    def collect_coverage(self, policy: LCovOutputPathPolicy, silent: int=1):
        self.cmd_executor.must_exec(f"{self.lcov_cmd} --no-checksum --capture --directory {self.source_dir} --output-file {policy.lcov_info_file}", silent=silent)

        if self.lcov_exclude_opts:
            merge_file = tempfile.NamedTemporaryFile(delete=False)
            merge_file_name = merge_file.name
        else:
            merge_file = None
            merge_file_name = policy.lcov_info_final_file

        if policy.lcov_base_file:
            policy.lcov_base_file = ' -a ' + policy.lcov_base_file
        self.cmd_executor.must_exec(f"{self.lcov_cmd} --no-checksum{policy.lcov_base_file} -a {policy.lcov_info_file} --output-file {merge_file_name}", silent=silent)            
        if self.lcov_exclude_opts:
            self.cmd_executor.must_exec(f"{self.lcov_cmd} --no-checksum -r {merge_file_name} {self.lcov_exclude_opts} --output-file {policy.lcov_info_final_file}", silent=silent)    
            os.unlink(merge_file.name)
        
        # llvm issue
        # https://github.com/linux-test-project/lcov/issues/30
        # policy.lcov_info_final_file
        # todo: function must not be ignored in format: int a() { return b; }
        with open(policy.lcov_info_final_file, 'r') as f:
            lines = list(f)
        with open(policy.lcov_info_final_file, 'w') as f:
            for line in filter_lcov(lines, verbose=True):
                f.write(line)

    # finial
    ### write out the final zero coverage and positive coverage reports
    # write_zero_cov(cov['zero'], cov_paths, cargs)
    # write_pos_cov(cov['pos'], cov_paths, cargs)

    # if not cargs.disable_lcov_web:
    #     lcov_gen_coverage(cov_paths, cargs)
    #     gen_web_cov_report(fuzz_dir, cov_paths, cargs)


class GenHtmlRunner(object):
    gen_html_path: str
    gen_html_opts: str

    def __init__(self, container: BuildContainer):
        self.gen_html_path = container.opts.gen_html_path
        self.gen_html_opts = ''
        if container.opts.enable_branch_coverage:
            self.gen_html_opts += ' --branch-coverage'
        self.cmd_executor = CommandExecutor(container)
    
    def gen_cov_report(self, p: GenHtmlOutputPathPolicy, silent:int=1):
        self.cmd_executor.exec(
            f"{self.gen_html_path}{self.gen_html_opts} --output-directory {p.gen_html_output_dir} {p.lcov_info_final_file}", silent=silent)

class BuildContainerImpl(BuildContainer):
    opts: object

    def __init__(self, opts):
        self.opts = opts
        self.type_protocols = dict()

    def register_impl(self, t: type, p: type=None):
        if p:
            self.type_protocols[p] = t
        self.type_protocols[t] = t

    def resolve(self, t: typing.Type[T]) -> T:
        return self.type_protocols[t](self)


class LoggerImpl(Logger):
    def __init__(self, container):
        pass

    def verbose(self, msg, log_obj=None):
        print(msg, log_obj)

    def info(self, msg, log_obj=None):
        print(msg, log_obj)

    def warn(self, msg, log_obj=None):
        print(msg, log_obj)

    def debug(self, msg, log_obj=None):
        print(msg, log_obj)

    def critical(self, msg, log_obj=None):
        print(msg, log_obj)


class InvalidOpts(Exception): pass


class Opts(object):
    fuzzer_path: str
    source_dir: str
    output_dir: str
    lcov_output_dir: str
    gen_html_output_dir: str
    enable_branch_coverage: bool
    lcov_follow_links: bool
    lcov_exclude_pattern: str
    lcov_path: str
    gen_html_path: str

    def __init__(self):
        self.lcov_path = 'lcov'
        self.gen_html_path = 'genhtml'
        # default False
        self.enable_branch_coverage = False
        self.lcov_follow_links = False
    
    def validate(self):
        if not self.lcov_path:
            return InvalidOpts("must set lcov_path, got empty string")
        if not self.gen_html_path:
            return InvalidOpts("must set gen_html_path, got empty string")
        if not self.fuzzer_path:
            return InvalidOpts("must set fuzzer_path, got empty string")
        if not self.source_dir:
            return InvalidOpts("must set source_dir, got empty string")
        if not self.output_dir:
            return InvalidOpts("must set output_dir, got empty string")
        if not self.lcov_output_dir:
            return InvalidOpts("must set lcov_output_dir, got empty string")
        if not self.gen_html_output_dir:
            return InvalidOpts("must set gen_html_output_dir, got empty string")
        if not self.gen_html_output_dir:
            return InvalidOpts("must set gen_html_output_dir, got empty string")
        return None

def parse_cmdline():

    # opts.output_dir = os.path.realpath('.material/fuzz-cov')

    p = argparse.ArgumentParser()

    p.add_argument("--fuzzer", type=str, required=True,
        help="Fuzzer Path (gcov instrumented)")
    p.add_argument("-s", "--src", type=str, required=True,
        help="Source root directory")
    p.add_argument("-o", "--out", type=str, required=True,
        help="Coverage output directory")
    p.add_argument("-c", "--corpus-dir", type=str, required=True,
        help="Corpus (inputs) Directory")

    p.add_argument("--lcov-follow-links", action='store_true', default=False,
        help="Follow links when searching .da files")
    p.add_argument("--enable-branch-coverage", action='store_true', default=False,
        help="Include branch coverage in code coverage reports (may be slow)")
    p.add_argument("--lcov-exclude-pattern", type=str, default="/usr/include/\\*",
        help="Set exclude pattern for lcov results")
    
    p.add_argument("--lcov-path", type=str,
            help="Path to lcov command", default="/usr/bin/lcov")
    p.add_argument("--gen-html-path", type=str,
            help="Path to genhtml command", default="/usr/bin/genhtml")
    
    p.add_argument("-v", "--verbose", action='store_true',
            help="Verbose mode", default=False)
    p.add_argument("-V", "--version", action='store_true',
            help="Print version and exit", default=False)
    p.add_argument("-q", "--quiet", action='store_true',
            help="Quiet mode", default=False)

    # p.add_argument("--disable-coverage-init", action='store_true',
    #         help="Disable initialization of code coverage counters at afl-cov startup",
    #         default=False)

    # p.add_argument("--gcov-check", action='store_true',
    #         help="Check to see if there is a binary in --coverage-cmd (or in --gcov-check-bin) has coverage support",
    #         default=False)
    # p.add_argument("--gcov-check-bin", type=str,
    #         help="Test a specific binary for code coverage support",
    #         default=False)
    # p.add_argument("--disable-gcov-check", type=str,
    #         help="Disable check for code coverage support",
    #         default=False)

    # p.add_argument("-O", "--overwrite", action='store_true',
    #         help="Overwrite existing coverage results", default=False)
    # p.add_argument("--validate-args", action='store_true',
    #         help="Validate args and exit", default=False)

    return p.parse_args()
 
def main():
    # Setup Environment Values
    opts = Opts()

    args = parse_cmdline()
    opts.lcov_path = args.lcov_path
    opts.gen_html_path = args.gen_html_path

    opts.fuzzer_path = args.fuzzer
    opts.source_dir = args.src
    opts.output_dir = args.out
    
    opts.lcov_exclude_pattern = args.lcov_exclude_pattern
    opts.enable_branch_coverage = args.enable_branch_coverage
    opts.lcov_follow_links = args.lcov_follow_links

    opts.lcov_output_dir = os.path.join(opts.output_dir, 'lcov')
    opts.gen_html_output_dir = os.path.join(opts.output_dir, 'web')

    maybe_err = opts.validate()
    if maybe_err is not None:
        raise maybe_err # pylint: disable-msg=E0702

    clean = True

    # create container
    container = BuildContainerImpl(opts)
    container.register_impl(LoggerImpl, Logger)
    container.register_impl(LibFuzzerInstanceExecutor, FuzzerExecutor)
    container.register_impl(LCovRunner)
    container.register_impl(LCovOutputPathPolicy)
    container.register_impl(GenHtmlRunner)
    container.register_impl(GenHtmlOutputPathPolicy)

    # create lcov components
    lcov_path_policy = container.resolve(LCovOutputPathPolicy)
    gen_html_path_policy = container.resolve(GenHtmlOutputPathPolicy)
    fuzzer_instance = container.resolve(FuzzerExecutor)
    lcov_runner = container.resolve(LCovRunner)
    gen_html_runner = container.resolve(GenHtmlRunner)

    # main logic
    cov_output_path = Path(opts.output_dir)
    cov_output_path.mkdir(parents=True, exist_ok=True)

    lcov_path_policy.initialize_file_structure(clean=clean)
    gen_html_path_policy.initialize_file_structure(clean=clean)

    lcov_runner.init_coverage_files(lcov_path_policy, silent=0)
    fuzzer_instance.exec_corpus_set(args.corpus_dir, silent=0)
    lcov_runner.collect_coverage(lcov_path_policy, silent=0)

    gen_html_path_policy.use_lcov_path_policy(lcov_path_policy)
    gen_html_runner.gen_cov_report(gen_html_path_policy, silent=0)


if __name__ == '__main__':
    main()

