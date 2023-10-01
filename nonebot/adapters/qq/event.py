from enum import Enum
from typing_extensions import override
from typing import Dict, Type, Tuple, TypeVar, Optional

from nonebot.utils import escape_tag

from nonebot.adapters import Event as BaseEvent

from .message import Message
from .models import Message as GuildMessage
from .models import Post, User, Guild, Reply, Member, Thread, Channel
from .models import (
    RichText,
    MessageDelete,
    MessageAudited,
    MessageReaction,
    ForumAuditResult,
    ThreadSourceInfo,
)

E = TypeVar("E", bound="Event")


class EventType(str, Enum):
    # Init Event
    READY = "READY"
    RESUMED = "RESUMED"

    # GUILDS
    GUILD_CREATE = "GUILD_CREATE"
    GUILD_UPDATE = "GUILD_UPDATE"
    GUILD_DELETE = "GUILD_DELETE"
    CHANNEL_CREATE = "CHANNEL_CREATE"
    CHANNEL_UPDATE = "CHANNEL_UPDATE"
    CHANNEL_DELETE = "CHANNEL_DELETE"

    # GUILD_MEMBERS
    GUILD_MEMBER_ADD = "GUILD_MEMBER_ADD"
    GUILD_MEMBER_UPDATE = "GUILD_MEMBER_UPDATE"
    GUILD_MEMBER_REMOVE = "GUILD_MEMBER_REMOVE"

    # GUILD_MESSAGES
    MESSAGE_CREATE = "MESSAGE_CREATE"
    MESSAGE_DELETE = "MESSAGE_DELETE"

    # GUILD_MESSAGE_REACTIONS
    MESSAGE_REACTION_ADD = "MESSAGE_REACTION_ADD"
    MESSAGE_REACTION_REMOVE = "MESSAGE_REACTION_REMOVE"

    # DIRECT_MESSAGE
    DIRECT_MESSAGE_CREATE = "DIRECT_MESSAGE_CREATE"
    DIRECT_MESSAGE_DELETE = "DIRECT_MESSAGE_DELETE"

    # MESSAGE_AUDIT
    MESSAGE_AUDIT_PASS = "MESSAGE_AUDIT_PASS"
    MESSAGE_AUDIT_REJECT = "MESSAGE_AUDIT_REJECT"

    # FORUM_EVENT
    FORUM_THREAD_CREATE = "FORUM_THREAD_CREATE"
    FORUM_THREAD_UPDATE = "FORUM_THREAD_UPDATE"
    FORUM_THREAD_DELETE = "FORUM_THREAD_DELETE"
    FORUM_POST_CREATE = "FORUM_POST_CREATE"
    FORUM_POST_DELETE = "FORUM_POST_DELETE"
    FORUM_REPLY_CREATE = "FORUM_REPLY_CREATE"
    FORUM_REPLY_DELETE = "FORUM_REPLY_DELETE"
    FORUM_PUBLISH_AUDIT_RESULT = "FORUM_PUBLISH_AUDIT_RESULT"

    # AUDIO_ACTION
    AUDIO_START = "AUDIO_START"
    AUDIO_FINISH = "AUDIO_FINISH"
    AUDIO_ON_MIC = "AUDIO_ON_MIC"
    AUDIO_OFF_MIC = "AUDIO_OFF_MIC"

    # AT_MESSAGES
    AT_MESSAGE_CREATE = "AT_MESSAGE_CREATE"
    PUBLIC_MESSAGE_DELETE = "PUBLIC_MESSAGE_DELETE"


class Event(BaseEvent):
    __type__: EventType

    @override
    def get_event_name(self) -> str:
        return self.__type__

    @override
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @override
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @override
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def get_session_id(self) -> str:
        raise ValueError("Event has no context!")

    @override
    def is_tome(self) -> bool:
        return False


EVENT_CLASSES: Dict[str, Type[Event]] = {}


def register_event_class(event_class: Type[E]) -> Type[E]:
    EVENT_CLASSES[event_class.__type__.value] = event_class
    return event_class


# Meta Event
class MetaEvent(Event):
    @override
    def get_type(self) -> str:
        return "meta_event"


@register_event_class
class ReadyEvent(MetaEvent):
    __type__ = EventType.READY
    version: int
    session_id: str
    user: User
    shard: Tuple[int, int]


@register_event_class
class ResumedEvent(MetaEvent):
    __type__ = EventType.RESUMED


# Guild Event
class GuildEvent(Event, Guild):
    op_user_id: str

    @override
    def get_type(self) -> str:
        return "notice"


@register_event_class
class GuildCreateEvent(GuildEvent):
    __type__ = EventType.GUILD_CREATE


@register_event_class
class GuildUpdateEvent(GuildEvent):
    __type__ = EventType.GUILD_UPDATE


@register_event_class
class GuildDeleteEvent(GuildEvent):
    __type__ = EventType.GUILD_DELETE


# Channel Event
class ChannelEvent(Event, Channel):
    op_user_id: str

    @override
    def get_type(self) -> str:
        return "notice"


@register_event_class
class ChannelCreateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_CREATE


@register_event_class
class ChannelUpdateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_UPDATE


@register_event_class
class ChannelDeleteEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_DELETE


# Guild Member Event
class GuildMemberEvent(Event, Member):
    guild_id: str
    op_user_id: str

    @override
    def get_type(self) -> str:
        return "notice"

    @override
    def get_user_id(self) -> str:
        return str(self.user.id)  # type: ignore

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Notice {getattr(self.user, 'username', None)}"
            f"@[Guild:{self.guild_id}] Roles:{self.roles}"
        )

    @override
    def get_session_id(self) -> str:
        return str(self.user.id)  # type: ignore


@register_event_class
class GuildMemberAddEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_ADD


@register_event_class
class GuildMemberUpdateEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_UPDATE


@register_event_class
class GuildMemberRemoveEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_REMOVE


# Message Event
class MessageEvent(Event, GuildMessage):
    to_me: bool = False

    reply: Optional[GuildMessage] = None
    """
    :说明: 消息中提取的回复消息，内容为 ``get_message_of_id`` API 返回结果

    :类型: ``Optional[MessageGet]``
    """

    @override
    def get_type(self) -> str:
        return "message"

    @override
    def get_user_id(self) -> str:
        return str(self.author.id)  # type: ignore

    @override
    def get_session_id(self) -> str:
        return str(self.author.id)  # type: ignore

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from "
            f"{getattr(self.author, 'username', None)}"
            f"@[Guild:{self.guild_id}/{self.channel_id}] "
            f"Roles:{getattr(self.member, 'roles', None)}: {self.get_message()}"
        )

    @override
    def get_message(self) -> Message:
        if not hasattr(self, "_message"):
            setattr(self, "_message", Message.from_guild_message(self))
        return getattr(self, "_message")

    @override
    def is_tome(self) -> bool:
        return self.to_me


@register_event_class
class MessageCreateEvent(MessageEvent):
    __type__ = EventType.MESSAGE_CREATE


@register_event_class
class MessageDeleteEvent(Event, MessageDelete):
    __type__ = EventType.MESSAGE_DELETE

    @override
    def get_type(self) -> str:
        return "notice"


@register_event_class
class AtMessageCreateEvent(MessageEvent):
    __type__ = EventType.AT_MESSAGE_CREATE
    to_me: bool = True


@register_event_class
class PublicMessageDeleteEvent(MessageDeleteEvent):
    __type__ = EventType.PUBLIC_MESSAGE_DELETE


@register_event_class
class DirectMessageCreateEvent(MessageEvent):
    __type__ = EventType.DIRECT_MESSAGE_CREATE
    to_me: bool = True

    @override
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from "
            f"{getattr(self.author, 'username', None)}: {self.get_message()}"
        )


@register_event_class
class DirectMessageDeleteEvent(MessageDeleteEvent):
    __type__ = EventType.DIRECT_MESSAGE_DELETE


# Message Audit Event
class MessageAuditEvent(Event, MessageAudited):
    @override
    def get_type(self) -> str:
        return "notice"


@register_event_class
class MessageAuditPassEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_PASS


@register_event_class
class MessageAuditRejectEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_REJECT


# Message Reaction Event
class MessageReactionEvent(Event, MessageReaction):
    @override
    def get_type(self) -> str:
        return "notice"

    @override
    def get_user_id(self) -> str:
        return str(self.user_id)

    @override
    def get_session_id(self) -> str:
        return str(self.user_id)


@register_event_class
class MessageReactionAddEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_ADD


@register_event_class
class MessageReactionRemoveEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_REMOVE


class ForumEvent(Event, ThreadSourceInfo):
    @override
    def get_type(self) -> str:
        return "notice"

    @override
    def get_user_id(self) -> str:
        return str(self.author_id)

    @override
    def get_session_id(self) -> str:
        return f"forum_{self.author_id}"


class ForumThreadEvent(ForumEvent, Thread[RichText]):
    ...


@register_event_class
class ForumThreadCreateEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_CREATE


@register_event_class
class ForumThreadUpdateEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_UPDATE


@register_event_class
class ForumThreadDeleteEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_DELETE


class ForumPostEvent(ForumEvent, Post):
    ...


@register_event_class
class ForumPostCreateEvent(ForumPostEvent):
    __type__ = EventType.FORUM_POST_CREATE


@register_event_class
class ForumPostDeleteEvent(ForumPostEvent):
    __type__ = EventType.FORUM_POST_DELETE


class ForumReplyEvent(ForumEvent, Reply):
    ...


@register_event_class
class ForumReplyCreateEvent(ForumReplyEvent):
    __type__ = EventType.FORUM_REPLY_CREATE


@register_event_class
class ForumReplyDeleteEvent(ForumReplyEvent):
    __type__ = EventType.FORUM_REPLY_DELETE


@register_event_class
class ForumPublishAuditResult(ForumEvent, ForumAuditResult):
    __type__ = EventType.FORUM_PUBLISH_AUDIT_RESULT


__all__ = [
    "EventType",
    "Event",
    "GuildEvent",
    "GuildCreateEvent",
    "GuildUpdateEvent",
    "GuildDeleteEvent",
    "ChannelEvent",
    "ChannelCreateEvent",
    "ChannelUpdateEvent",
    "ChannelDeleteEvent",
    "GuildMemberEvent",
    "GuildMemberAddEvent",
    "GuildMemberUpdateEvent",
    "GuildMemberRemoveEvent",
    "MessageEvent",
    "MessageCreateEvent",
    "MessageDeleteEvent",
    "AtMessageCreateEvent",
    "PublicMessageDeleteEvent",
    "DirectMessageCreateEvent",
    "DirectMessageDeleteEvent",
    "MessageAuditEvent",
    "MessageAuditPassEvent",
    "MessageAuditRejectEvent",
    "MessageReactionEvent",
    "MessageReactionAddEvent",
    "MessageReactionRemoveEvent",
]
