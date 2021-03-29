
import typing

from .container import BuildContainer
from .logger import Logger
from .utils import Protocol

class FuzzerExecutor(Protocol):
    def __init__(self, container: BuildContainer):
        raise NotImplementedError
    
    def exec_one_file(self, case_file: str, silent: int=1):
        raise NotImplementedError
    
    def exec_corpus_set(self, corpus_dir: str, silent: int=1):
        raise NotImplementedError
