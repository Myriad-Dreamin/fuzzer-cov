
import typing
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol

cT = typing.TypeVar('T')
class BuildContainer(Protocol):
    T = cT
    opts: object

    def register_impl(self, t: type, p: type=None):
        raise NotImplementedError

    def resolve(self, t: typing.Type[cT]) -> cT:
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
