
from pathlib import Path
import subprocess
import os
import tempfile

from fuzzer_cov.core import BuildContainer, CommandExecutor

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
        self.cmd_executor = container.resolve(CommandExecutor)
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
