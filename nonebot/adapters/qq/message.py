import re
from io import BytesIO
from pathlib import Path
from dataclasses import dataclass
from typing_extensions import override
from typing import TYPE_CHECKING, Type, Union, Iterable, Optional, TypedDict, overload

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment

from .utils import escape, unescape
from .models import Message as GuildMessage
from .models import (
    MessageArk,
    MessageEmbed,
    MessageKeyboard,
    MessageMarkdown,
    MessageReference,
)


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @override
    def get_message_class(cls) -> Type["Message"]:
        return Message

    @staticmethod
    def text(content: str) -> "Text":
        return Text("text", {"text": content})

    @staticmethod
    def emoji(id: str) -> "Emoji":
        return Emoji("emoji", data={"id": id})

    @staticmethod
    def mention_user(user_id: str) -> "MentionUser":
        return MentionUser("mention_user", {"user_id": str(user_id)})

    @staticmethod
    def mention_channel(channel_id: str) -> "MentionChannel":
        return MentionChannel("mention_channel", {"channel_id": str(channel_id)})

    @staticmethod
    def mention_everyone() -> "MentionEveryone":
        return MentionEveryone("mention_everyone", {})

    @staticmethod
    def image(url: str) -> "Attachment":
        return Attachment("attachment", data={"url": url})

    @staticmethod
    def file_image(data: Union[bytes, BytesIO, Path]) -> "LocalImage":
        if isinstance(data, BytesIO):
            data = data.getvalue()
        elif isinstance(data, Path):
            data = data.read_bytes()
        return LocalImage("file_image", data={"content": data})

    @staticmethod
    def ark(ark: MessageArk) -> "Ark":
        return Ark("ark", data={"ark": ark})

    @staticmethod
    def embed(embed: MessageEmbed) -> "Embed":
        return Embed("embed", data={"embed": embed})

    @staticmethod
    def markdown(markdown: Union[str, MessageMarkdown]) -> "Markdown":
        return Markdown(
            "markdown",
            data={
                "markdown": MessageMarkdown(content=markdown)
                if isinstance(markdown, str)
                else markdown
            },
        )

    @staticmethod
    def keyboard(keyboard: MessageKeyboard) -> "Keyboard":
        return Keyboard("keyboard", data={"keyboard": keyboard})

    @overload
    @staticmethod
    def reference(reference: MessageReference) -> "Reference":
        ...

    @overload
    @staticmethod
    def reference(reference: str, ignore_error: Optional[bool] = None) -> "Reference":
        ...

    @staticmethod
    def reference(
        reference: Union[str, MessageReference], ignore_error: Optional[bool] = None
    ) -> "Reference":
        if isinstance(reference, MessageReference):
            return Reference("reference", data={"reference": reference})

        return Reference(
            "reference",
            data={
                "reference": MessageReference(
                    message_id=reference, ignore_get_message_error=ignore_error
                )
            },
        )

    @override
    def __add__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return Message(self) + (
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @override
    def __radd__(
        self, other: Union[str, "MessageSegment", Iterable["MessageSegment"]]
    ) -> "Message":
        return (
            MessageSegment.text(other) if isinstance(other, str) else Message(other)
        ) + self

    @override
    def is_text(self) -> bool:
        return self.type == "text"


class _TextData(TypedDict):
    text: str


@dataclass
class Text(MessageSegment):
    if TYPE_CHECKING:
        data: _TextData

    @override
    def __str__(self) -> str:
        return escape(self.data["text"])


class _EmojiData(TypedDict):
    id: str


@dataclass
class Emoji(MessageSegment):
    if TYPE_CHECKING:
        data: _EmojiData

    @override
    def __str__(self) -> str:
        return f"<emoji:{self.data['id']}>"


class _MentionUserData(TypedDict):
    user_id: str


@dataclass
class MentionUser(MessageSegment):
    if TYPE_CHECKING:
        data: _MentionUserData

    @override
    def __str__(self) -> str:
        return f"<@{self.data['user_id']}>"


class _MentionChannelData(TypedDict):
    channel_id: str


@dataclass
class MentionChannel(MessageSegment):
    if TYPE_CHECKING:
        data: _MentionChannelData

    @override
    def __str__(self) -> str:
        return f"<#{self.data['channel_id']}>"


class _MentionEveryoneData(TypedDict):
    pass


@dataclass
class MentionEveryone(MessageSegment):
    if TYPE_CHECKING:
        data: _MentionEveryoneData

    @override
    def __str__(self) -> str:
        return "@everyone"


class _AttachmentData(TypedDict):
    url: str


@dataclass
class Attachment(MessageSegment):
    if TYPE_CHECKING:
        data: _AttachmentData

    @override
    def __str__(self) -> str:
        return f"<attachment:{self.data['url']}>"


class _LocalImageData(TypedDict):
    content: bytes


@dataclass
class LocalImage(MessageSegment):
    if TYPE_CHECKING:
        data: _LocalImageData

    @override
    def __str__(self) -> str:
        return "<local_image>"


class _EmbedData(TypedDict):
    embed: MessageEmbed


@dataclass
class Embed(MessageSegment):
    if TYPE_CHECKING:
        data: _EmbedData

    @override
    def __str__(self) -> str:
        return f"<embed:{self.data['embed']!r}>"


class _ArkData(TypedDict):
    ark: MessageArk


@dataclass
class Ark(MessageSegment):
    if TYPE_CHECKING:
        data: _ArkData

    @override
    def __str__(self) -> str:
        return f"<ark:{self.data['ark']!r}>"


class _ReferenceData(TypedDict):
    reference: MessageReference


@dataclass
class Reference(MessageSegment):
    if TYPE_CHECKING:
        data: _ReferenceData

    @override
    def __str__(self) -> str:
        return f"<reference:{self.data['reference'].message_id}>"


class _MarkdownData(TypedDict):
    markdown: MessageMarkdown


@dataclass
class Markdown(MessageSegment):
    if TYPE_CHECKING:
        data: _MarkdownData

    @override
    def __str__(self) -> str:
        return f"<markdown:{self.data['markdown']!r}>"


class _KeyboardData(TypedDict):
    keyboard: MessageKeyboard


@dataclass
class Keyboard(MessageSegment):
    if TYPE_CHECKING:
        data: _KeyboardData

    @override
    def __str__(self) -> str:
        return f"<keyboard:{self.data['keyboard']!r}>"


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override
    def get_segment_class(cls) -> Type[MessageSegment]:
        return MessageSegment

    @override
    def __add__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super().__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @override
    def __radd__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> "Message":
        return super().__radd__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @staticmethod
    @override
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
        if message.mention_everyone:
            msg.append(MessageSegment.mention_everyone())
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
