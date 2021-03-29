
from .utils import Protocol
from .container import BuildContainer

class Logger(Protocol):
    def __init__(self, container: BuildContainer):
        raise NotImplementedError

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
