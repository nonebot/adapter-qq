from functools import partial
from typing_extensions import ParamSpec, Concatenate
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Type,
    Generic,
    TypeVar,
    Callable,
    Optional,
    Awaitable,
    overload,
)

from nonebot.utils import logger_wrapper

if TYPE_CHECKING:
    from .bot import Bot

B = TypeVar("B", bound="Bot")
R = TypeVar("R")
P = ParamSpec("P")

log = logger_wrapper("QQ")


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unescape(s: str) -> str:
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")


def exclude_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}


class API(Generic[B, P, R]):
    def __init__(self, func: Callable[Concatenate[B, P], Awaitable[R]]) -> None:
        self.func = func

    def __set_name__(self, owner: Type[B], name: str) -> None:
        self.name = name

    @overload
    def __get__(self, obj: None, objtype: Type[B]) -> "API[B, P, R]": ...

    @overload
    def __get__(
        self, obj: B, objtype: Optional[Type[B]]
    ) -> Callable[P, Awaitable[R]]: ...

    def __get__(
        self, obj: Optional[B], objtype: Optional[Type[B]] = None
    ) -> "API[B, P, R] | Callable[P, Awaitable[R]]":
        if obj is None:
            return self

        return partial(obj.call_api, self.name)  # type: ignore

    async def __call__(self, inst: B, *args: P.args, **kwds: P.kwargs) -> R:
        return await self.func(inst, *args, **kwds)
