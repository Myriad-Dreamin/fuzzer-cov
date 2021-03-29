
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
