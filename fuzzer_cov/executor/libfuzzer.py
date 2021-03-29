
from fuzzer_cov.core import BuildContainer
from fuzzer_cov.core import FuzzerExecutor
from fuzzer_cov.core import Logger
from fuzzer_cov.core.executor import CommandExecutor

class LibFuzzerInstanceExecutor(FuzzerExecutor):
    fuzzer_path: str
    logger: Logger

    def __init__(self, container: BuildContainer):
        self.fuzzer_path = container.opts.fuzzer_path
        self.logger = container.resolve(Logger)
        self.cmd_executor = container.resolve(CommandExecutor)

    def exec_one_file(self, case_file: str, silent: int=1):
        return self.cmd_executor.exec(f"{self.fuzzer_path} {case_file} -runs=1 -timeout=600", silent)

    def exec_corpus_set(self, corpus_dir: str, silent: int=1):
        return self.cmd_executor.exec(f"{self.fuzzer_path} {corpus_dir} -runs=1 -timeout=600", silent)
