
import typing

from .utils import Protocol

cT = typing.TypeVar('T')
class BuildContainer(Protocol):
    T = cT
    opts: object

    def register_impl(self, t: type, p: type=None):
        raise NotImplementedError

    def resolve(self, t: typing.Type[cT]) -> cT:
        raise NotImplementedError

class BuildContainerImpl(BuildContainer):
    opts: object

    def __init__(self, opts):
        self.opts = opts
        self.type_protocols = dict()

    def register_impl(self, t: type, p: type=None):
        if p:
            self.type_protocols[p] = t
        self.type_protocols[t] = t

    def resolve(self, t: typing.Type[BuildContainer.T]) -> BuildContainer.T:
        return self.type_protocols[t](self)
