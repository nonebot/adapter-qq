import asyncio
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .event import MessageAuditEvent


class AuditResultStore:
    def __init__(self) -> None:
        self._futures: dict[str, asyncio.Future] = {}

    def add_result(self, result: "MessageAuditEvent"):
        audit_id = result.audit_id
        if not audit_id:
            raise ValueError("audit_id cannot be empty")
        if future := self._futures.get(audit_id):
            future.set_result(result)

    async def fetch(
        self, audit_id: str, timeout: Optional[float] = None
    ) -> "MessageAuditEvent":
        future = asyncio.get_event_loop().create_future()
        self._futures[audit_id] = future
        try:
            return await asyncio.wait_for(future, timeout)
        finally:
            del self._futures[audit_id]


audit_result = AuditResultStore()
