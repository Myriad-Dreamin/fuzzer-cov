
from pathlib import Path

from fuzzer_cov.core import BuildContainer, CommandExecutor
from .lcov import LCovOutputPathPolicy

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

class GenHtmlRunner(object):
    gen_html_path: str
    gen_html_opts: str

    def __init__(self, container: BuildContainer):
        self.gen_html_path = container.opts.gen_html_path
        self.gen_html_opts = ''
        if container.opts.enable_branch_coverage:
            self.gen_html_opts += ' --branch-coverage'
        self.cmd_executor = container.resolve(CommandExecutor)
    
    def gen_cov_report(self, p: GenHtmlOutputPathPolicy, silent:int=1):
        self.cmd_executor.exec(
            f"{self.gen_html_path}{self.gen_html_opts} --output-directory {p.gen_html_output_dir} {p.lcov_info_final_file}", silent=silent)
