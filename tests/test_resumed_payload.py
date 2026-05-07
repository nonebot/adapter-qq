from nonebot.compat import type_validate_json

from nonebot.adapters.qq.adapter import Adapter
from nonebot.adapters.qq.models import Dispatch, PayloadType


def test_resumed_payload_is_dispatch() -> None:
    payload = type_validate_json(
        PayloadType, '{"op":0,"s":2002,"t":"RESUMED","d":""}'
    )

    assert isinstance(payload, Dispatch)
    assert payload.sequence == 2002
    assert payload.type == "RESUMED"
    assert payload.data == ""


def test_resumed_payload_calls_on_dispatch() -> None:
    class DummyBot:
        def __init__(self) -> None:
            self.dispatched_payload = None

        def on_dispatch(self, payload: Dispatch) -> None:
            self.dispatched_payload = payload

    bot = DummyBot()
    payload = Adapter.data_to_payload(bot, '{"op":0,"s":2002,"t":"RESUMED","d":""}')

    assert isinstance(payload, Dispatch)
    assert bot.dispatched_payload is payload
