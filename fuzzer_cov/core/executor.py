
from .utils import Protocol
from .container import BuildContainer

class CommandExecutor(Protocol):
    def __init__(self, container: BuildContainer):
        raise NotImplementedError

    def must_exec(self, cmd, silent: int=1):
        raise NotImplementedError
    
    def exec(self, cmd, silent: int=1):
        raise NotImplementedError

class FuzzerExecutor(Protocol):
    def __init__(self, container: BuildContainer):
        raise NotImplementedError
    
    def exec_one_file(self, case_file: str, silent: int=1):
        raise NotImplementedError
    
    def exec_corpus_set(self, corpus_dir: str, silent: int=1):
        raise NotImplementedError
