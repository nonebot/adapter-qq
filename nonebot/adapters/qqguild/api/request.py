import json
from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from nonebot.drivers import Request
from pydantic.typing import is_none_type, display_as_type
from pydantic import Extra, BaseModel, BaseConfig, create_model

from .model import *

if TYPE_CHECKING:
    from nonebot.adapters.qqguild.bot import Bot
    from nonebot.adapters.qqguild.adapter import Adapter


async def _request(adapter: "Adapter", bot: "Bot", request: Request) -> Any:
    data = await adapter.request(request)
    assert 200 <= data.status_code < 300
    return data.content and json.loads(data.content)


def _exclude_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
