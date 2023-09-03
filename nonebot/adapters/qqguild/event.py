from enum import Enum
from typing import Dict, Type, Tuple, Optional

from nonebot.adapters import Event as BaseEvent
from nonebot.typing import overrides
from nonebot.utils import escape_tag

from .api import Message as GuildMessage
from .api import MessageGet, MessageDelete, MessageAudited, MessageReaction
from .api import User, Guild, Member, Channel
from .api import ForumObject, ForumThread, ForumPost, ForumReply, \
    ForumAuditResult, RichText
from .message import Message


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

    @overrides(BaseEvent)
    def get_event_name(self) -> str:
        return self.__type__

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(str(self.dict()))

    @overrides(BaseEvent)
    def get_message(self) -> Message:
        raise ValueError("Event has no message!")

    @overrides(BaseEvent)
    def get_user_id(self) -> str:
        raise ValueError("Event has no context!")

    @overrides(BaseEvent)
    def get_session_id(self) -> str:
        raise ValueError("Event has no context!")

    @overrides(BaseEvent)
    def is_tome(self) -> bool:
        return False


# Meta Event
class MetaEvent(Event):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "meta_event"


class ReadyEvent(MetaEvent):
    __type__ = EventType.READY
    version: int
    session_id: str
    user: User
    shard: Tuple[int, int]


class ResumedEvent(MetaEvent):
    __type__ = EventType.RESUMED


# Guild Event
class GuildEvent(Event, Guild):
    op_user_id: str

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class GuildCreateEvent(GuildEvent):
    __type__ = EventType.GUILD_CREATE


class GuildUpdateEvent(GuildEvent):
    __type__ = EventType.GUILD_UPDATE


class GuildDeleteEvent(GuildEvent):
    __type__ = EventType.GUILD_DELETE


# Channel Event
class ChannelEvent(Event, Channel):
    op_user_id: str

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class ChannelCreateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_CREATE


class ChannelUpdateEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_UPDATE


class ChannelDeleteEvent(ChannelEvent):
    __type__ = EventType.CHANNEL_DELETE


# Guild Member Event
class GuildMemberEvent(Event, Member):
    guild_id: str
    op_user_id: str

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"

    @overrides(Event)
    def get_user_id(self) -> str:
        return str(self.user.id)  # type: ignore

    @overrides(Event)
    def get_event_description(self) -> str:
        return escape_tag(
            f"Notice {getattr(self.user, 'username', None)}"
            f"@[Guild:{self.guild_id}] Roles:{self.roles}"
        )

    @overrides(Event)
    def get_session_id(self) -> str:
        return str(self.user.id)  # type: ignore


class GuildMemberAddEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_ADD


class GuildMemberUpdateEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_UPDATE


class GuildMemberRemoveEvent(GuildMemberEvent):
    __type__ = EventType.GUILD_MEMBER_REMOVE


# Message Event
class MessageEvent(Event, GuildMessage):
    to_me: bool = False

    reply: Optional[MessageGet] = None
    """
    :说明: 消息中提取的回复消息，内容为 ``get_message_of_id`` API 返回结果

    :类型: ``Optional[MessageGet]``
    """

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "message"

    @overrides(Event)
    def get_user_id(self) -> str:
        return str(self.author.id)  # type: ignore

    @overrides(Event)
    def get_session_id(self) -> str:
        return str(self.author.id)  # type: ignore

    @overrides(BaseEvent)
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from "
            f"{getattr(self.author, 'username', None)}"
            f"@[Guild:{self.guild_id}/{self.channel_id}] "
            f"Roles:{getattr(self.member, 'roles', None)}: {self.get_message()}"
        )

    @overrides(Event)
    def get_message(self) -> Message:
        if not hasattr(self, "_message"):
            setattr(self, "_message", Message.from_guild_message(self))
        return getattr(self, "_message")

    @overrides(Event)
    def is_tome(self) -> bool:
        return self.to_me


class MessageCreateEvent(MessageEvent):
    __type__ = EventType.MESSAGE_CREATE


class MessageDeleteEvent(Event, MessageDelete):
    __type__ = EventType.MESSAGE_DELETE

    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class AtMessageCreateEvent(MessageEvent):
    __type__ = EventType.AT_MESSAGE_CREATE
    to_me: bool = True


class PublicMessageDeleteEvent(MessageDeleteEvent):
    __type__ = EventType.PUBLIC_MESSAGE_DELETE


class DirectMessageCreateEvent(MessageEvent):
    __type__ = EventType.DIRECT_MESSAGE_CREATE
    to_me: bool = True

    @overrides(MessageEvent)
    def get_event_description(self) -> str:
        return escape_tag(
            f"Message {self.id} from "
            f"{getattr(self.author, 'username', None)}: {self.get_message()}"
        )


class DirectMessageDeleteEvent(MessageDeleteEvent):
    __type__ = EventType.DIRECT_MESSAGE_DELETE


# Message Audit Event
class MessageAuditEvent(Event, MessageAudited):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"


class MessageAuditPassEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_PASS


class MessageAuditRejectEvent(MessageAuditEvent):
    __type__ = EventType.MESSAGE_AUDIT_REJECT


# Message Reaction Event
class MessageReactionEvent(Event, MessageReaction):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"

    @overrides(Event)
    def get_user_id(self) -> str:
        return str(self.user_id)

    @overrides(Event)
    def get_session_id(self) -> str:
        return str(self.user_id)


class MessageReactionAddEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_ADD


class MessageReactionRemoveEvent(MessageReactionEvent):
    __type__ = EventType.MESSAGE_REACTION_REMOVE


class ForumEvent(Event, ForumObject):
    @overrides(BaseEvent)
    def get_type(self) -> str:
        return "notice"

    @overrides(Event)
    def get_user_id(self) -> str:
        return str(self.author_id)

    @overrides(Event)
    def get_session_id(self) -> str:
        return str(self.author_id)


class ForumThreadEvent(ForumEvent, ForumThread[RichText]):
    ...


class ForumThreadCreateEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_CREATE


class ForumThreadUpdateEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_UPDATE


class ForumThreadDeleteEvent(ForumThreadEvent):
    __type__ = EventType.FORUM_THREAD_DELETE


class ForumPostEvent(ForumEvent, ForumPost):
    ...


class ForumPostCreateEvent(ForumPostEvent):
    __type__ = EventType.FORUM_POST_CREATE


class ForumPostDeleteEvent(ForumPostEvent):
    __type__ = EventType.FORUM_POST_DELETE


class ForumReplyEvent(ForumEvent, ForumReply):
    ...


class ForumReplyCreateEvent(ForumReplyEvent):
    __type__ = EventType.FORUM_REPLY_CREATE


class ForumReplyDeleteEvent(ForumReplyEvent):
    __type__ = EventType.FORUM_REPLY_DELETE


class ForumPublishAuditResult(ForumEvent, ForumAuditResult):
    __type__ = EventType.FORUM_PUBLISH_AUDIT_RESULT


# TODO: Audio Event

event_classes: Dict[str, Type[Event]] = {
    EventType.READY.value: ReadyEvent,
    EventType.RESUMED.value: ResumedEvent,
    EventType.GUILD_CREATE.value: GuildCreateEvent,
    EventType.GUILD_DELETE.value: GuildDeleteEvent,
    EventType.GUILD_UPDATE.value: GuildUpdateEvent,
    EventType.CHANNEL_CREATE.value: ChannelCreateEvent,
    EventType.CHANNEL_DELETE.value: ChannelDeleteEvent,
    EventType.CHANNEL_UPDATE.value: ChannelUpdateEvent,
    EventType.GUILD_MEMBER_ADD.value: GuildMemberAddEvent,
    EventType.GUILD_MEMBER_UPDATE.value: GuildMemberUpdateEvent,
    EventType.GUILD_MEMBER_REMOVE.value: GuildMemberRemoveEvent,
    EventType.MESSAGE_CREATE.value: MessageCreateEvent,
    EventType.MESSAGE_DELETE.value: MessageDeleteEvent,
    EventType.AT_MESSAGE_CREATE.value: AtMessageCreateEvent,
    EventType.PUBLIC_MESSAGE_DELETE.value: PublicMessageDeleteEvent,
    EventType.DIRECT_MESSAGE_CREATE.value: DirectMessageCreateEvent,
    EventType.DIRECT_MESSAGE_DELETE.value: DirectMessageDeleteEvent,
    EventType.MESSAGE_AUDIT_PASS.value: MessageAuditPassEvent,
    EventType.MESSAGE_AUDIT_REJECT.value: MessageAuditRejectEvent,
    EventType.MESSAGE_REACTION_ADD.value: MessageReactionAddEvent,
    EventType.MESSAGE_REACTION_REMOVE.value: MessageReactionRemoveEvent,
    EventType.FORUM_THREAD_CREATE.value: ForumThreadCreateEvent,
    EventType.FORUM_THREAD_UPDATE.value: ForumThreadUpdateEvent,
    EventType.FORUM_THREAD_DELETE.value: ForumThreadDeleteEvent,
    EventType.FORUM_POST_CREATE.value: ForumPostCreateEvent,
    EventType.FORUM_POST_DELETE.value: ForumPostDeleteEvent,
    EventType.FORUM_REPLY_CREATE.value: ForumReplyCreateEvent,
    EventType.FORUM_REPLY_DELETE.value: ForumReplyDeleteEvent,
    EventType.FORUM_PUBLISH_AUDIT_RESULT.value: ForumPublishAuditResult,
}

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
