from typing import Any, Type, Union, Mapping, Iterable, cast

from nonebot.typing import overrides

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import escape, unescape


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @overrides(BaseMessageSegment)
    def __str__(self) -> str:
        type_ = self.type

        # process special types
        if type_ == "text":
            return escape(self.data.get("text", ""))
        elif type_ == "emoji":
            return f"<emoji:{self.data['id']}>"
        elif type_ == "mention_user":
            return f"<@{self.data['user_id']}>"
        elif type_ == "mention_channel":
            return f"<#{self.data['channel_id']}>"
        return ""

    @staticmethod
    def emoji(id: int) -> "MessageSegment":
        return MessageSegment("emoji", data={"id": str(id)})

    @staticmethod
    def mention_user(user_id: str) -> "MessageSegment":
        return MessageSegment("mention_user", {"user_id": user_id})

    @staticmethod
    def mention_channel(channel_id: str) -> "MessageSegment":
        return MessageSegment("mention_channel", {"channel_id": channel_id})

    @staticmethod
    def text(content: str) -> "MessageSegment":
        return MessageSegment("text", {"text": content})

    @overrides(BaseMessageSegment)
    def is_text(self) -> bool:
        return self.type == "text"


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @overrides(BaseMessage)
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @overrides(BaseMessage)
    def __add__(self, other: Union[str, Mapping, Iterable[Mapping]]) -> "Message":
        return super(Message, self).__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @overrides(BaseMessage)
    def __radd__(self, other: Union[str, Mapping, Iterable[Mapping]]) -> "Message":
        return super(Message, self).__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @staticmethod
    @overrides(BaseMessage)
    def _construct(
        msg: Union[str, Mapping, Iterable[Mapping]]
    ) -> Iterable[MessageSegment]:
        if isinstance(msg, Mapping):
            msg = cast(Mapping[str, Any], msg)
            yield MessageSegment(msg["type"], msg.get("data") or {})
            return
        elif isinstance(msg, Iterable) and not isinstance(msg, str):
            for seg in msg:
                yield MessageSegment(seg["type"], seg.get("data") or {})
            return
        elif isinstance(msg, str):
            # FIXME
            yield MessageSegment.text(str(msg))
