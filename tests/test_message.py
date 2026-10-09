from nonebot.adapters.qq.message import Message
from nonebot.adapters.qq.models import GroupMentionEveryone, GroupMentionUser, QQMessage


def _qq_message(content: str, mentions=None) -> QQMessage:
    return QQMessage(
        id="1",
        content=content,
        timestamp="2024-01-01T00:00:00+00:00",
        mentions=mentions,
    )


def test_construct_recognizes_new_mention_everyone_tag():
    message = Message("before<qqbot-at-everyone />after")

    assert [(seg.type, seg.data) for seg in message] == [
        ("text", {"text": "before"}),
        ("mention_everyone", {}),
        ("text", {"text": "after"}),
    ]


def test_construct_no_longer_recognizes_legacy_at_all_tag():
    # 旧版 <@all>/<@id> 标签格式已经不再下发（维护者确认），不再做兜底识别，
    # 原样保留成文本
    message = Message("<@all>hi")

    assert [(seg.type, seg.data) for seg in message] == [("text", {"text": "<@all>hi"})]


def test_construct_no_longer_strips_literal_at_everyone():
    # 旧版字面量 "@everyone" 兜底清理逻辑已移除，原样保留成文本
    message = Message("hi @everyone bye")

    assert [(seg.type, seg.data) for seg in message] == [
        ("text", {"text": "hi @everyone bye"})
    ]


def test_from_qq_message_recognizes_structured_mention_everyone():
    # GroupMentionEveryone 结构化数据下发"@全体成员"，content 文本里没有对应标签
    message = _qq_message(
        "hello",
        mentions=[GroupMentionEveryone(scope="all", is_you=True, username="bot")],
    )

    result = Message.from_qq_message(message)

    assert result["mention_everyone"] is not None
    assert [(seg.type, seg.data) for seg in result] == [
        ("mention_everyone", {}),
        ("text", {"text": "hello"}),
    ]


def test_from_qq_message_does_not_duplicate_mention_everyone():
    # content 里已经带了 <qqbot-at-everyone />，mentions 结构化数据也标了同一件事
    message = _qq_message(
        "<qqbot-at-everyone />hello",
        mentions=[GroupMentionEveryone(scope="all", is_you=True, username="bot")],
    )

    result = Message.from_qq_message(message)

    assert len(result["mention_everyone"]) == 1


def test_from_qq_message_still_handles_mention_user():
    message = _qq_message(
        "hi",
        mentions=[
            GroupMentionUser(
                scope="single",
                bot=False,
                id="123",
                is_you=False,
                member_openid="123",
                username="alice",
            )
        ],
    )

    result = Message.from_qq_message(message)

    ats = result["mention_user"]
    assert len(ats) == 1
    assert ats[0].data["user_id"] == "123"
    assert ats[0].data["username"] == "alice"
