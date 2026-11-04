import pytest

from nonebot.adapters.qq import Bot, Message, MessageSegment
from nonebot.adapters.qq.exception import MessageSegmentConflict
from nonebot.adapters.qq.models import (
    MessageActionButton,
    MessageArk,
    MessageEmbed,
    MessageKeyboard,
    MessageMarkdown,
    MessagePromptKeyboard,
    PromptContent,
    PromptKeyboardModel,
)


def _prompt_keyboard() -> MessagePromptKeyboard:
    return MessagePromptKeyboard(
        keyboard=PromptKeyboardModel(content=PromptContent(rows=[]))
    )


def test_message_segment_conflict_is_exported_from_package_root():
    from nonebot.adapters.qq import MessageSegmentConflict as ExportedConflict

    assert ExportedConflict is MessageSegmentConflict


# --- 违反互斥限制的组合：应当报错 ---


def test_markdown_with_text_conflict():
    message = MessageSegment.text("hello") + MessageSegment.markdown("world")
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_template_markdown_with_mention_conflict():
    # 模板 markdown 没有自由文本位置，即使是"可合并"的标签类型也无法合并
    message = MessageSegment.mention_user("123") + MessageSegment.markdown(
        MessageMarkdown(template_id=1)
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_template_markdown_with_another_markdown_conflict():
    message = MessageSegment.markdown(
        MessageMarkdown(template_id=1)
    ) + MessageSegment.markdown("b")
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_ark_with_markdown_conflict():
    message = MessageSegment.ark(MessageArk(template_id=1)) + MessageSegment.markdown(
        "a"
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_ark_with_text_conflict():
    message = MessageSegment.ark(MessageArk(template_id=1)) + MessageSegment.text("hi")
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


def test_ark_with_mention_conflict():
    message = MessageSegment.ark(
        MessageArk(template_id=1)
    ) + MessageSegment.mention_user("1")
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


def test_media_with_markdown_conflict():
    message = MessageSegment.image(
        "https://example.com/a.png"
    ) + MessageSegment.markdown("a")
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_media_with_ark_conflict():
    message = MessageSegment.image("https://example.com/a.png") + MessageSegment.ark(
        MessageArk(template_id=1)
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


def test_media_with_embed_conflict():
    message = MessageSegment.image("https://example.com/a.png") + MessageSegment.embed(
        MessageEmbed(prompt="p")
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_media_with_keyboard_conflict():
    message = MessageSegment.image(
        "https://example.com/a.png"
    ) + MessageSegment.keyboard(MessageKeyboard(id="1"))
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


def test_multiple_media_segments_conflict():
    message = MessageSegment.image("https://example.com/a.png") + MessageSegment.video(
        "https://example.com/a.mp4"
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_multiple_ark_segments_conflict():
    # 不涉及 markdown/text，单独测 ark 自己的 [-1] 静默丢弃
    message = MessageSegment.ark(MessageArk(template_id=1)) + MessageSegment.ark(
        MessageArk(template_id=2)
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_multiple_embed_segments_conflict():
    message = MessageSegment.embed(MessageEmbed(prompt="a")) + MessageSegment.embed(
        MessageEmbed(prompt="b")
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_multiple_reference_segments_conflict():
    message = MessageSegment.reference("111") + MessageSegment.reference("222")
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_multiple_keyboard_segments_conflict():
    message = (
        MessageSegment.markdown("hi")
        + MessageSegment.keyboard(MessageKeyboard(id="1"))
        + MessageSegment.keyboard(MessageKeyboard(id="2"))
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


def test_multiple_stream_segments_conflict():
    # stream 只在 c2c 里被支持，group 会在更早的规则里直接拒绝
    message = MessageSegment.stream(1, None, 0) + MessageSegment.stream(1, None, 1)
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_multiple_prompt_keyboard_segments_conflict():
    message = (
        MessageSegment.markdown("hi")
        + MessageSegment.prompt_keyboard(_prompt_keyboard())
        + MessageSegment.prompt_keyboard(_prompt_keyboard())
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_multiple_action_button_segments_conflict():
    message = (
        MessageSegment.markdown("hi")
        + MessageSegment.action_button(MessageActionButton())
        + MessageSegment.action_button(MessageActionButton())
    )
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_keyboard_without_markdown_conflict():
    message = Message(MessageSegment.keyboard(MessageKeyboard(id="1")))
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_c2c_prompt_keyboard_without_markdown_conflict():
    message = Message(MessageSegment.prompt_keyboard(_prompt_keyboard()))
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_c2c_action_button_without_markdown_conflict():
    message = Message(MessageSegment.action_button(MessageActionButton()))
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=False)


def test_group_rejects_stream_segment():
    message = Message(MessageSegment.stream(1, None, 0))
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


def test_group_rejects_prompt_keyboard_segment():
    message = Message(MessageSegment.prompt_keyboard(_prompt_keyboard()))
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


def test_group_rejects_action_button_segment():
    message = Message(MessageSegment.action_button(MessageActionButton()))
    with pytest.raises(MessageSegmentConflict):
        Bot._resolve_message_conflicts(message, is_group=True)


# --- 合法组合：不应该报错 ---


def test_markdown_alone_is_allowed():
    message = Message(MessageSegment.markdown("hello"))
    result = Bot._resolve_message_conflicts(message, is_group=False)
    assert result == message
    Bot._resolve_message_conflicts(message, is_group=True)


def test_template_markdown_alone_is_allowed():
    message = Message(MessageSegment.markdown(MessageMarkdown(template_id=1)))
    result = Bot._resolve_message_conflicts(message, is_group=False)
    assert result == message


def test_text_alone_is_allowed():
    message = Message(MessageSegment.text("hello"))
    Bot._resolve_message_conflicts(message, is_group=False)
    Bot._resolve_message_conflicts(message, is_group=True)


def test_ark_alone_is_allowed():
    message = Message(MessageSegment.ark(MessageArk(template_id=1)))
    Bot._resolve_message_conflicts(message, is_group=False)
    Bot._resolve_message_conflicts(message, is_group=True)


def test_single_media_segment_is_allowed():
    message = Message(MessageSegment.image("https://example.com/a.png"))
    Bot._resolve_message_conflicts(message, is_group=False)
    Bot._resolve_message_conflicts(message, is_group=True)


def test_c2c_prompt_keyboard_with_markdown_is_allowed():
    message = MessageSegment.markdown("hello") + MessageSegment.prompt_keyboard(
        _prompt_keyboard()
    )
    Bot._resolve_message_conflicts(message, is_group=False)


def test_c2c_action_button_with_markdown_is_allowed():
    message = MessageSegment.markdown("hello") + MessageSegment.action_button(
        MessageActionButton()
    )
    Bot._resolve_message_conflicts(message, is_group=False)


def test_c2c_stream_without_markdown_is_allowed():
    # stream 只在 send_to_c2c 里被支持，不受这里任何一条规则限制
    message = Message(MessageSegment.stream(1, None, 0))
    Bot._resolve_message_conflicts(message, is_group=False)


# --- markdown + 结构化标签段：自动合并，而不是报错 ---


def test_markdown_with_mention_user_is_merged():
    message = MessageSegment.mention_user("123") + MessageSegment.markdown("world")
    result = Bot._resolve_message_conflicts(message, is_group=True)

    assert [(seg.type, seg.data) for seg in result] == [
        ("markdown", {"markdown": MessageMarkdown(content="<@123>world")})
    ]


def test_markdown_with_mention_everyone_and_emoji_is_merged():
    message = (
        MessageSegment.markdown("before ")
        + MessageSegment.mention_everyone()
        + MessageSegment.emoji("1")
    )
    result = Bot._resolve_message_conflicts(message, is_group=False)

    assert len(result) == 1
    assert result[0].type == "markdown"
    assert result[0].data["markdown"].content == "before @everyone<emoji:1>"


def test_multiple_pure_markdown_segments_are_merged():
    message = MessageSegment.markdown("a") + MessageSegment.markdown("b")
    result = Bot._resolve_message_conflicts(message, is_group=False)

    assert len(result) == 1
    assert result[0].type == "markdown"
    assert result[0].data["markdown"].content == "ab"


def test_markdown_mention_markdown_preserves_original_order():
    message = (
        MessageSegment.markdown("a")
        + MessageSegment.mention_user("1")
        + MessageSegment.markdown("b")
    )
    result = Bot._resolve_message_conflicts(message, is_group=False)

    assert len(result) == 1
    assert result[0].data["markdown"].content == "a<@1>b"


def test_merge_preserves_unrelated_segments():
    message = (
        MessageSegment.markdown("hi")
        + MessageSegment.mention_user("1")
        + MessageSegment.keyboard(MessageKeyboard(id="1"))
    )
    result = Bot._resolve_message_conflicts(message, is_group=True)

    assert [seg.type for seg in result] == ["markdown", "keyboard"]
    assert result[0].data["markdown"].content == "hi<@1>"
