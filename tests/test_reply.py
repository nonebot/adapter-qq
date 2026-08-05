import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from nonebot.adapters.qq import Adapter
from nonebot.adapters.qq.bot import _check_reply
from nonebot.adapters.qq.event import GroupMessageCreateEvent
from nonebot.adapters.qq.models import Dispatch


def create_event(
    *,
    content: str | None = None,
    mention_id: str = "REPLIED_USER",
    mention_is_you: bool = False,
    ref_msg_idx: str | None = "REFIDX_REPLY=",
    reply_author: dict | None = None,
) -> GroupMessageCreateEvent:
    with Path(__file__).with_name("events.json").open(encoding="utf-8") as file:
        payload_data = json.load(file)

    data = payload_data["d"]
    data["content"] = f" <@{mention_id}> zssm" if content is None else content
    data["mentions"][0]["id"] = mention_id
    data["mentions"][0]["member_openid"] = mention_id
    data["mentions"][0]["is_you"] = mention_is_you
    ext = ["msg_idx=REFIDX_CURRENT=", "auth_token=test"]
    if ref_msg_idx:
        ext.insert(0, f"ref_msg_idx={ref_msg_idx}")
    data["message_scene"]["ext"] = ext
    reply = data["msg_elements"][0]
    if reply_author is not None:
        reply["author"] = reply_author
    event = Adapter.payload_to_event(
        Dispatch(
            opcode=payload_data["op"],
            data=data,
            type=payload_data["t"],
            id=payload_data["id"],
        )
    )
    assert isinstance(event, GroupMessageCreateEvent)
    return event


@pytest.mark.asyncio
async def test_group_reply_removes_automatic_mention():
    event = create_event()
    bot = SimpleNamespace(self_info=SimpleNamespace(id="BOT", username="bot"))

    await _check_reply(bot, event)

    assert event.reply is not None
    assert event.reply.content == "都登不上"
    assert [(segment.type, segment.data) for segment in event.get_message()] == [
        ("text", {"text": "zssm"})
    ]


@pytest.mark.asyncio
async def test_group_reply_requires_matching_reference_index():
    event = create_event(ref_msg_idx="REFIDX_OTHER=")
    original_message = event.get_message().copy()
    bot = SimpleNamespace(self_info=SimpleNamespace(id="BOT", username="bot"))

    await _check_reply(bot, event)

    assert event.reply is None
    assert event.get_message() == original_message


@pytest.mark.asyncio
async def test_group_reply_preserves_mismatched_leading_mention():
    event = create_event(
        reply_author={
            "id": "ACTUAL_AUTHOR",
            "member_openid": "ACTUAL_AUTHOR",
            "username": "actual author",
            "bot": False,
        }
    )
    original_message = event.get_message().copy()
    bot = SimpleNamespace(self_info=SimpleNamespace(id="BOT", username="bot"))

    await _check_reply(bot, event)

    assert event.reply is not None
    assert event.get_message() == original_message


@pytest.mark.asyncio
async def test_group_reply_to_bot_remains_to_me():
    event = create_event(mention_id="BOT", mention_is_you=True)
    bot = SimpleNamespace(self_info=SimpleNamespace(id="BOT", username="bot"))

    await _check_reply(bot, event)

    assert event.to_me is True
    assert event.get_message().extract_plain_text() == "zssm"


@pytest.mark.asyncio
async def test_group_message_without_reference_is_not_a_reply():
    event = create_event(ref_msg_idx=None)
    original_message = event.get_message().copy()
    bot = SimpleNamespace(self_info=SimpleNamespace(id="BOT", username="bot"))

    await _check_reply(bot, event)

    assert event.reply is None
    assert event.get_message() == original_message
