import json
from typing import Optional

from nonebot.drivers import Response
from nonebot.exception import ActionFailed as BaseActionFailed
from nonebot.exception import AdapterException
from nonebot.exception import ApiNotAvailable as BaseApiNotAvailable
from nonebot.exception import NetworkError as BaseNetworkError
from nonebot.exception import NoLogException as BaseNoLogException

from .store import audit_result


class QQAdapterException(AdapterException):
    def __init__(self):
        super().__init__("qq")


class NoLogException(BaseNoLogException, QQAdapterException):
    pass


class ActionFailed(BaseActionFailed, QQAdapterException):
    def __init__(self, response: Response):
        self.response = response

        self.body: Optional[dict] = None
        if response.content:
            try:
                self.body = json.loads(response.content)
            except Exception:
                pass

    @property
    def status_code(self) -> int:
        return self.response.status_code

    @property
    def code(self) -> Optional[int]:
        return None if self.body is None else self.body.get("code", None)

    @property
    def message(self) -> Optional[str]:
        return None if self.body is None else self.body.get("message", None)

    @property
    def data(self) -> Optional[dict]:
        return None if self.body is None else self.body.get("data", None)

    @property
    def trace_id(self) -> Optional[str]:
        return self.response.headers.get("X-Tps-trace-ID", None)

    def __repr__(self) -> str:
        args = ("code", "message", "data", "trace_id")
        return (
            f"<ActionFailed: {self.status_code}, "
            + ", ".join(f"{k}={v}" for k in args if (v := getattr(self, k)) is not None)
            + ">"
        )

    def __str__(self):
        return self.__repr__()


class UnauthorizedException(ActionFailed):
    pass


class RateLimitException(ActionFailed):
    pass


class NetworkError(BaseNetworkError, QQAdapterException):
    def __init__(self, msg: Optional[str] = None):
        super().__init__()
        self.msg: Optional[str] = msg
        """错误原因"""

    def __repr__(self):
        return f"<NetWorkError message={self.msg}>"

    def __str__(self):
        return self.__repr__()


class ApiNotAvailable(BaseApiNotAvailable, QQAdapterException):
    pass


class AuditException(QQAdapterException):
    """消息审核"""

    def __init__(self, audit_id: str):
        super().__init__()
        self.audit_id = audit_id

    async def get_audit_result(self, timeout: Optional[float] = None):
        """获取审核结果"""
        return await audit_result.fetch(self.audit_id, timeout)
