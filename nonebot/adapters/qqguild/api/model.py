from typing import List, Optional
from datetime import date, datetime

from pydantic import BaseModel


class Guild(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    icon: Optional[str] = None
    owner_id: Optional[int] = None
    owner: Optional[bool] = None
    member_count: Optional[int] = None
    max_members: Optional[int] = None
    description: Optional[str] = None
    joined_at: Optional[str] = None


class User(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    avatar: Optional[str] = None
    bot: Optional[bool] = None
    union_openid: Optional[str] = None
    union_user_account: Optional[str] = None


class ChannelCreate(BaseModel):
    name: str
    type: int
    sub_type: int
    position: Optional[int] = None
    parent_id: Optional[int] = None
    private_type: Optional[int] = None
    private_user_ids: Optional[List[int]] = None


class Channel(BaseModel):
    id: Optional[int] = None
    guild_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[int] = None
    sub_type: Optional[int] = None
    position: Optional[int] = None
    parent_id: Optional[str] = None
    owner_id: Optional[int] = None
    private_type: Optional[int] = None
    speak_permission: Optional[int] = None
    application_id: Optional[str] = None


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[int] = None
    sub_type: Optional[int] = None
    position: Optional[int] = None
    parent_id: Optional[int] = None
    private_type: Optional[int] = None


class Member(BaseModel):
    user: Optional[User] = None
    nick: Optional[str] = None
    roles: Optional[List[int]] = None
    joined_at: Optional[datetime] = None


class DeleteMemberBody(BaseModel):
    add_blacklist: Optional[bool] = None


class Role(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[int] = None
    hoist: Optional[int] = None
    number: Optional[int] = None
    member_limit: Optional[int] = None


class GetGuildRolesReturn(BaseModel):
    guild_id: Optional[str] = None
    roles: Optional[List[Role]] = None
    role_num_limit: Optional[str] = None


class PostGuildRoleBody(BaseModel):
    name: str
    color: Optional[float] = None
    hoist: Optional[float] = None


class GuildRole(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    color: Optional[float] = None
    hoist: Optional[float] = None
    number: Optional[float] = None
    member_limit: Optional[float] = None


class PostGuildRoleReturn(BaseModel):
    role_id: Optional[str] = None
    role: Optional[GuildRole] = None


class PatchGuildRoleBody(BaseModel):
    name: Optional[str] = None
    color: Optional[float] = None
    hoist: Optional[float] = None


class PatchGuildRoleReturn(BaseModel):
    guild_id: Optional[str] = None
    role_id: Optional[str] = None
    role: Optional[GuildRole] = None


class PutGuildMemberRoleBody(BaseModel):
    id: Optional[str] = None


class DeleteGuildMemberRoleBody(BaseModel):
    id: Optional[str] = None


class ChannelPermissions(BaseModel):
    channel_id: Optional[int] = None
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    permissions: Optional[str] = None


class PutChannelPermissionsBody(BaseModel):
    add: Optional[str] = None
    remove: Optional[str] = None


class PutChannelRolesPermissionsBody(BaseModel):
    add: Optional[str] = None
    remove: Optional[str] = None


class MessageAttachment(BaseModel):
    url: Optional[str] = None


class MessageEmbedThumbnail(BaseModel):
    url: Optional[str] = None


class MessageEmbedField(BaseModel):
    name: Optional[str] = None


class MessageEmbed(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    thumbnail: Optional[MessageEmbedThumbnail] = None
    fields: Optional[List[MessageEmbedField]] = None


class MessageArkObjKv(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None


class MessageArkObj(BaseModel):
    obj_kv: Optional[List[MessageArkObjKv]] = None


class MessageArkKv(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None
    obj: Optional[List[MessageArkObj]] = None


class MessageArk(BaseModel):
    template_id: Optional[int] = None
    kv: Optional[List[MessageArkKv]] = None


class MessageReference(BaseModel):
    message_id: Optional[str] = None
    ignore_get_message_error: Optional[bool] = None


class Message(BaseModel):
    id: Optional[str] = None
    channel_id: Optional[int] = None
    guild_id: Optional[int] = None
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
    edited_timestamp: Optional[datetime] = None
    mention_everyone: Optional[bool] = None
    author: Optional[User] = None
    attachments: Optional[List[MessageAttachment]] = None
    embeds: Optional[List[MessageEmbed]] = None
    mentions: Optional[List[User]] = None
    member: Optional[Member] = None
    ark: Optional[MessageArk] = None
    seq: Optional[int] = None
    seq_in_channel: Optional[str] = None
    message_reference: Optional[MessageReference] = None


class MessageSend(BaseModel):
    content: Optional[str] = None
    embed: Optional[MessageEmbed] = None
    ark: Optional[MessageArk] = None
    message_reference: Optional[MessageReference] = None
    image: Optional[str] = None
    msg_id: Optional[str] = None


class PostDmsBody(BaseModel):
    recipient_id: str
    source_guild_id: str


class PatchGuildMuteBody(BaseModel):
    mute_end_timestamp: Optional[str] = None
    mute_seconds: Optional[str] = None


class PatchGuildMemberMuteBody(BaseModel):
    mute_end_timestamp: Optional[str] = None
    mute_seconds: Optional[str] = None


class PostGuildAnnouncesBody(BaseModel):
    message_id: str
    channel_id: str


class PostChannelAnnouncesBody(BaseModel):
    message_id: str


class Announces(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_id: Optional[str] = None


class GetSchedulesBody(BaseModel):
    since: Optional[int] = None


class ScheduleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_timestamp: int
    end_timestamp: int
    creator: Optional[Member] = None
    jump_channel_id: Optional[int] = None
    remind_type: str


class Schedule(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    start_timestamp: Optional[int] = None
    end_timestamp: Optional[int] = None
    creator: Optional[Member] = None
    jump_channel_id: Optional[int] = None
    remind_type: Optional[str] = None


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_timestamp: Optional[int] = None
    end_timestamp: Optional[int] = None
    creator: Optional[Member] = None
    jump_channel_id: Optional[int] = None
    remind_type: Optional[str] = None


class AudioControl(BaseModel):
    audio_url: Optional[str] = None
    text: Optional[str] = None
    status: Optional[int] = None


class APIPermissionDemandIdentify(BaseModel):
    path: Optional[str] = None
    name: Optional[str] = None


class PostApiPermissionDemandBody(BaseModel):
    channel_id: Optional[str] = None
    api_identify: Optional[APIPermissionDemandIdentify] = None
    desc: Optional[str] = None


class UrlGetReturn(BaseModel):
    url: Optional[str] = None


class SessionStartLimit(BaseModel):
    total: Optional[int] = None
    remaining: Optional[int] = None
    reset_after: Optional[int] = None
    max_concurrency: Optional[int] = None


class ShardUrlGetReturn(BaseModel):
    url: Optional[str] = None
    shards: Optional[int] = None
    session_start_limit: Optional[SessionStartLimit] = None


class PinsMessage(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    message_ids: Optional[List[str]] = None


class MessageAudited(BaseModel):
    audit_id: Optional[str] = None
    message_id: Optional[str] = None
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    audit_time: Optional[datetime] = None
    create_time: Optional[datetime] = None
    seq_in_channel: Optional[str] = None


class DMS(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[str] = None
    create_time: Optional[int] = None


class Emoji(BaseModel):
    id: Optional[str] = None
    type: Optional[int] = None


class ReactionTarget(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None


class MessageReaction(BaseModel):
    user_id: Optional[int] = None
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    target: Optional[ReactionTarget] = None
    emoji: Optional[Emoji] = None


class APIPermission(BaseModel):
    path: Optional[str] = None
    method: Optional[str] = None
    desc: Optional[str] = None
    auth_status: Optional[int] = None


class APIPermissionDemand(BaseModel):
    guild_id: Optional[int] = None
    channel_id: Optional[int] = None
    api_identify: Optional[APIPermissionDemandIdentify] = None
    title: Optional[str] = None
    desc: Optional[str] = None
