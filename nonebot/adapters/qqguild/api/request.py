import json
from typing import TYPE_CHECKING, Any, Dict

from nonebot.drivers import Request

from nonebot.adapters.qqguild.exception import (
    ActionFailed,
    NetworkError,
    AuditException,
    ApiNotAvailable,
    RateLimitException,
    UnauthorizedException,
    QQGuildAdapterException,
)

from .model import *

if TYPE_CHECKING:
    from nonebot.adapters.qqguild.bot import Bot
    from nonebot.adapters.qqguild.adapter import Adapter


async def _request(adapter: "Adapter", bot: "Bot", request: Request) -> Any:
    try:
        data = await adapter.request(request)
        if data.status_code == 201 or data.status_code == 202:
            if data.content and (content := json.loads(data.content)):
                audit_id = (
                    content.get("data", {})
                    .get("message_audit", {})
                    .get("audit_id", None)
                )
                if audit_id:
                    raise AuditException(audit_id)
            raise ActionFailed(data)
        elif 200 <= data.status_code < 300:
            return data.content and json.loads(data.content)
        elif data.status_code == 401:
            raise UnauthorizedException(data)
        elif data.status_code in (404, 405):
            raise ApiNotAvailable
        elif data.status_code == 429:
            raise RateLimitException(data)
        else:
            raise ActionFailed(data)
    except QQGuildAdapterException:
        raise
    except Exception as e:
        raise NetworkError("API request failed") from e


def _exclude_none(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if v is not None}
