import re
from typing import Any, Type, Tuple, Union, Iterable

from nonebot.typing import overrides

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import escape, unescape


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @staticmethod
    def emoji(id: int) -> "Emoji":
        return Emoji("emoji", data={"id": str(id)})

    @staticmethod
    def mention_user(user_id: str) -> "MentionUser":
        return MentionUser("mention_user", {"user_id": user_id})

    @staticmethod
    def mention_channel(channel_id: str) -> "MentionChannel":
        return MentionChannel("mention_channel", {"channel_id": channel_id})

    @staticmethod
    def text(content: str) -> "Text":
        return Text("text", {"text": content})

    @overrides(BaseMessageSegment)
    def is_text(self) -> bool:
        return self.type == "text"


class Text(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return escape(self.data["text"])


class Emoji(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<emoji:{self.data['id']}>"


class MentionUser(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<@{self.data['user_id']}>"


class MentionEveryone(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return "@everyone"


class MentionChannel(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"#<{self.data['channel_id']}>"


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @overrides(BaseMessage)
    def __add__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super(Message, self).__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @overrides(BaseMessage)
    def __radd__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super(Message, self).__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @staticmethod
    @overrides(BaseMessage)
    def _construct(msg: str) -> Iterable[MessageSegment]:
        text_begin = 0
        for embed in re.finditer(
            r"\<@!?(?P<id>\w+?)\>",
            msg,
        ):
            yield Text("text", {"text": msg[text_begin : embed.pos + embed.start()]})
            text_begin = embed.pos + embed.end()
            yield MentionUser("mention_user", {"user_id": embed.group("id")})
        yield Text("text", {"text": msg[text_begin:]})
