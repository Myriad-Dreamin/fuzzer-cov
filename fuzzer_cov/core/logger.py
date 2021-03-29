
from .utils import Protocol

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
