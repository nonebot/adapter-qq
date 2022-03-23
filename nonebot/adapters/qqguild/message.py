import re
from typing import Any, Type, Tuple, Union, Iterable

from nonebot.typing import overrides

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import escape, unescape
from .api import Message as GuildMessage
from .api import MessageArk, MessageEmbed


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @overrides(BaseMessageSegment)
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @staticmethod
    def ark(ark: MessageArk) -> "Ark":
        return Ark("ark", data={"ark": ark})

    @staticmethod
    def embed(embed: MessageEmbed) -> "Embed":
        return Embed("embed", data={"embed": embed})

    @staticmethod
    def emoji(id: str) -> "Emoji":
        return Emoji("emoji", data={"id": id})

    @staticmethod
    def image(url: str) -> "Attachment":
        return Attachment("attachment", data={"url": url})

    @staticmethod
    def mention_user(user_id: int) -> "MentionUser":
        return MentionUser("mention_user", {"user_id": str(user_id)})

    @staticmethod
    def mention_channel(channel_id: int) -> "MentionChannel":
        return MentionChannel("mention_channel", {"channel_id": str(channel_id)})

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
        return f"<#{self.data['channel_id']}>"


class Attachment(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<attachment:{self.data['url']}>"


class Embed(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<embed:{self.data['embed']}>"


class Ark(MessageSegment):
    @overrides(MessageSegment)
    def __str__(self) -> str:
        return f"<ark:{self.data['ark']}>"


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
            r"\<(?P<type>(?:@|#|emoji:))!?(?P<id>\w+?)\>",
            msg,
        ):
            content = msg[text_begin : embed.pos + embed.start()]
            if content:
                yield Text("text", {"text": unescape(content)})
            text_begin = embed.pos + embed.end()
            if embed.group("type") == "@":
                yield MentionUser("mention_user", {"user_id": embed.group("id")})
            elif embed.group("type") == "#":
                yield MentionChannel(
                    "mention_channel", {"channel_id": embed.group("id")}
                )
            else:
                yield Emoji("emoji", {"id": embed.group("id")})
        content = msg[text_begin:]
        if content:
            yield Text("text", {"text": unescape(msg[text_begin:])})

    @classmethod
    def from_guild_message(cls, message: GuildMessage) -> "Message":
        msg = Message()
        if message.content:
            msg.extend(Message(message.content))
        if message.attachments:
            msg.extend(
                Attachment("attachment", data={"url": seg.url})
                for seg in message.attachments
                if seg.url
            )
        if message.embeds:
            msg.extend(Embed("embed", data={"embed": seg}) for seg in message.embeds)
        if message.ark:
            msg.append(Ark("ark", data={"ark": message.ark}))
        return msg

    def extract_content(self) -> str:
        return "".join(
            str(seg)
            for seg in self
            if seg.type
            in ("text", "emoji", "mention_user", "mention_everyone", "mention_channel")
        )
