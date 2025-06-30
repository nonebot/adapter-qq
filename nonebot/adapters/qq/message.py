from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re
from typing import TYPE_CHECKING, Literal, Optional, TypedDict, Union, overload
from typing_extensions import Self, override

from nonebot.adapters import Message as BaseMessage
from nonebot.adapters import MessageSegment as BaseMessageSegment
from nonebot.compat import type_validate_python

from .models import Attachment as QQAttachment
from .models import Message as GuildMessage
from .models import (
    MessageActionButton,
    MessageArk,
    MessageEmbed,
    MessageKeyboard,
    MessageMarkdown,
    MessagePromptKeyboard,
    MessageReference,
    MessageStream,
    QQMessage,
)
from .utils import escape, unescape


class MessageSegment(BaseMessageSegment["Message"]):
    @classmethod
    @override
    def get_message_class(cls) -> type["Message"]:
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
        return Attachment("image", data={"url": url})

    @staticmethod
    def file_image(data: Union[bytes, BytesIO, Path]) -> "LocalAttachment":
        if isinstance(data, BytesIO):
            data = data.getvalue()
        elif isinstance(data, Path):
            data = data.read_bytes()
        return LocalAttachment("file_image", data={"content": data})

    @staticmethod
    def audio(url: str) -> "Attachment":
        return Attachment("audio", data={"url": url})

    @staticmethod
    def file_audio(data: Union[bytes, BytesIO, Path]) -> "LocalAttachment":
        if isinstance(data, BytesIO):
            data = data.getvalue()
        elif isinstance(data, Path):
            data = data.read_bytes()
        return LocalAttachment("file_audio", data={"content": data})

    @staticmethod
    def video(url: str) -> "Attachment":
        return Attachment("video", data={"url": url})

    @staticmethod
    def file_video(data: Union[bytes, BytesIO, Path]) -> "LocalAttachment":
        if isinstance(data, BytesIO):
            data = data.getvalue()
        elif isinstance(data, Path):
            data = data.read_bytes()
        return LocalAttachment("file_video", data={"content": data})

    @staticmethod
    def file(url: str) -> "Attachment":
        return Attachment("file", data={"url": url})

    @staticmethod
    def file_file(data: Union[bytes, BytesIO, Path]) -> "LocalAttachment":
        if isinstance(data, BytesIO):
            data = data.getvalue()
        elif isinstance(data, Path):
            data = data.read_bytes()
        return LocalAttachment("file_file", data={"content": data})

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
                "markdown": (
                    MessageMarkdown(content=markdown)
                    if isinstance(markdown, str)
                    else markdown
                )
            },
        )

    @staticmethod
    def keyboard(keyboard: MessageKeyboard) -> "Keyboard":
        return Keyboard("keyboard", data={"keyboard": keyboard})

    @overload
    @staticmethod
    def reference(reference: MessageReference) -> "Reference": ...

    @overload
    @staticmethod
    def reference(
        reference: str, ignore_error: Optional[bool] = None
    ) -> "Reference": ...

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

    @staticmethod
    def stream(
        state: Literal[1, 10, 11, 20],
        _id: Optional[str],
        index: int,
        reset: Optional[bool] = None,
    ) -> "Stream":
        _data = {
            "state": state,
            "index": index,
        }
        if _id is not None:
            _data["id"] = _id

        if reset is not None:
            _data["reset"] = reset

        return Stream("stream", data={"stream": MessageStream(**_data)})

    @staticmethod
    def prompt_keyboard(prompt_keyboard: MessagePromptKeyboard) -> "PromptKeyboard":
        return PromptKeyboard(
            "prompt_keyboard", data={"prompt_keyboard": prompt_keyboard}
        )

    @staticmethod
    def action_button(action_button: MessageActionButton) -> "ActionButton":
        return ActionButton("action_button", data={"action_button": action_button})

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

    @classmethod
    @override
    def _validate(cls, value) -> Self:
        if isinstance(value, cls):
            return value
        if isinstance(value, MessageSegment):
            raise ValueError(f"Type {type(value)} can not be converted to {cls}")
        if not isinstance(value, dict):
            raise ValueError(f"Expected dict for MessageSegment, got {type(value)}")
        if "type" not in value:
            raise ValueError(
                f"Expected dict with 'type' for MessageSegment, got {value}"
            )
        _type = value["type"]
        if _type not in SEGMENT_TYPE_MAP:
            raise ValueError(f"Invalid MessageSegment type: {_type}")
        segment_type = SEGMENT_TYPE_MAP[_type]

        # casting value to subclass of MessageSegment
        if cls is MessageSegment:
            return type_validate_python(segment_type, value)
        # init segment instance directly if type matched
        if cls is segment_type:
            return segment_type(type=_type, data=value.get("data", {}))
        raise ValueError(f"Segment type {_type!r} can not be converted to {cls}")


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
        return f"<attachment[{self.type}]:{self.data['url']}>"


class _LocalAttachmentData(TypedDict):
    content: bytes


@dataclass
class LocalAttachment(MessageSegment):
    if TYPE_CHECKING:
        data: _LocalAttachmentData

    @override
    def __str__(self) -> str:
        return f"<local_attachment[{self.type}]>"


class _EmbedData(TypedDict):
    embed: MessageEmbed


@dataclass
class Embed(MessageSegment):
    if TYPE_CHECKING:
        data: _EmbedData

    @override
    def __str__(self) -> str:
        return f"<embed:{self.data['embed']!r}>"

    @classmethod
    @override
    def _validate(cls, value) -> Self:
        instance = super()._validate(value)
        if "embed" not in instance.data:
            raise ValueError(
                f"Expected dict with 'embed' in 'data' for Embed, got {value}"
            )
        if not isinstance(embed := instance.data["embed"], MessageEmbed):
            instance.data["embed"] = type_validate_python(MessageEmbed, embed)
        return instance


class _ArkData(TypedDict):
    ark: MessageArk


@dataclass
class Ark(MessageSegment):
    if TYPE_CHECKING:
        data: _ArkData

    @override
    def __str__(self) -> str:
        return f"<ark:{self.data['ark']!r}>"

    @classmethod
    @override
    def _validate(cls, value) -> Self:
        instance = super()._validate(value)
        if "ark" not in instance.data:
            raise ValueError(f"Expected dict with 'ark' in 'data' for Ark, got {value}")
        if not isinstance(ark := instance.data["ark"], MessageArk):
            instance.data["ark"] = type_validate_python(MessageArk, ark)
        return instance


class _ReferenceData(TypedDict):
    reference: MessageReference


@dataclass
class Reference(MessageSegment):
    if TYPE_CHECKING:
        data: _ReferenceData

    @override
    def __str__(self) -> str:
        return f"<reference:{self.data['reference'].message_id}>"

    @classmethod
    @override
    def _validate(cls, value) -> Self:
        instance = super()._validate(value)
        if "reference" not in instance.data:
            raise ValueError(
                f"Expected dict with 'reference' in 'data' for Reference, got {value}"
            )
        if not isinstance(reference := instance.data["reference"], MessageReference):
            instance.data["reference"] = type_validate_python(
                MessageReference, reference
            )
        return instance


class _MarkdownData(TypedDict):
    markdown: MessageMarkdown


@dataclass
class Markdown(MessageSegment):
    if TYPE_CHECKING:
        data: _MarkdownData

    @override
    def __str__(self) -> str:
        return f"<markdown:{self.data['markdown']!r}>"

    @classmethod
    @override
    def _validate(cls, value) -> Self:
        instance = super()._validate(value)
        if "markdown" not in instance.data:
            raise ValueError(
                f"Expected dict with 'markdown' in 'data' for Markdown, got {value}"
            )
        if not isinstance(markdown := instance.data["markdown"], MessageMarkdown):
            instance.data["markdown"] = type_validate_python(MessageMarkdown, markdown)
        return instance


class _KeyboardData(TypedDict):
    keyboard: MessageKeyboard


@dataclass
class Keyboard(MessageSegment):
    if TYPE_CHECKING:
        data: _KeyboardData

    @override
    def __str__(self) -> str:
        return f"<keyboard:{self.data['keyboard']!r}>"

    @classmethod
    @override
    def _validate(cls, value) -> Self:
        instance = super()._validate(value)
        if "keyboard" not in instance.data:
            raise ValueError(
                f"Expected dict with 'keyboard' in 'data' for Keyboard, got {value}"
            )
        if not isinstance(keyboard := instance.data["keyboard"], MessageKeyboard):
            instance.data["keyboard"] = type_validate_python(MessageKeyboard, keyboard)
        return instance


SEGMENT_TYPE_MAP: dict[str, type[MessageSegment]] = {
    "text": Text,
    "emoji": Emoji,
    "mention_user": MentionUser,
    "mention_channel": MentionChannel,
    "mention_everyone": MentionEveryone,
    "image": Attachment,
    "file_image": LocalAttachment,
    "audio": Attachment,
    "file_audio": LocalAttachment,
    "video": Attachment,
    "file_video": LocalAttachment,
    "file": Attachment,
    "file_file": LocalAttachment,
    "ark": Ark,
    "embed": Embed,
    "markdown": Markdown,
    "keyboard": Keyboard,
    "reference": Reference,
}


class _ActionButtonData(TypedDict):
    action_button: MessageActionButton


@dataclass
class ActionButton(MessageSegment):
    if TYPE_CHECKING:
        data: _ActionButtonData

    @override
    def __str__(self) -> str:
        return f"<action_button:{self.data['action_button']!r}>"


class _PromptKeyboardData(TypedDict):
    prompt_keyboard: MessagePromptKeyboard


@dataclass
class PromptKeyboard(MessageSegment):
    if TYPE_CHECKING:
        data: _PromptKeyboardData

    @override
    def __str__(self) -> str:
        return f"<prompt_keyboard:{self.data['prompt_keyboard']!r}>"


class _StreamData(TypedDict):
    stream: MessageStream


@dataclass
class Stream(MessageSegment):
    if TYPE_CHECKING:
        data: _StreamData

    @override
    def __str__(self) -> str:
        return f"<stream:{self.data['stream']!r}>"


class Message(BaseMessage[MessageSegment]):
    @classmethod
    @override
    def get_segment_class(cls) -> type[MessageSegment]:
        return MessageSegment

    @override
    def __add__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> Self:
        return super().__add__(
            MessageSegment.text(other) if isinstance(other, str) else other
        )

    @override
    def __radd__(
        self, other: Union[str, MessageSegment, Iterable[MessageSegment]]
    ) -> Self:
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
    def from_guild_message(cls, message: GuildMessage) -> Self:
        msg = cls()
        if message.mention_everyone:
            msg.append(MessageSegment.mention_everyone())
        if message.content:
            msg.extend(Message(message.content))
        if message.attachments:
            msg.extend(
                MessageSegment.image(seg.url) for seg in message.attachments if seg.url
            )
        if message.embeds:
            msg.extend(Embed("embed", data={"embed": seg}) for seg in message.embeds)
        if message.ark:
            msg.append(Ark("ark", data={"ark": message.ark}))
        return msg

    @classmethod
    def from_qq_message(cls, message: QQMessage) -> Self:
        msg = cls()
        if message.content:
            msg.extend(Message(message.content))
        if message.attachments:

            def content_type(seg: QQAttachment):
                ct = seg.content_type.split("/", maxsplit=1)[0]
                if ct in {"image", "audio", "file", "video"}:
                    return ct
                return "file"

            msg.extend(
                Attachment(
                    content_type(seg),
                    data={"url": seg.url},
                )
                for seg in message.attachments
                if seg.url
            )
        return msg

    def extract_content(self, escape_text: bool = True) -> str:
        return "".join(
            seg.data["text"] if not escape_text and seg.type == "text" else str(seg)
            for seg in self
            if seg.type
            in ("text", "emoji", "mention_user", "mention_everyone", "mention_channel")
        )

    @override
    def extract_plain_text(self) -> str:
        return "".join(seg.data["text"] for seg in self if seg.is_text())
