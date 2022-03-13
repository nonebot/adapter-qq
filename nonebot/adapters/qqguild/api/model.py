from typing import List

from pydantic import BaseModel


class Guild(BaseModel):
    id: str = None
    name: str = None
    icon: str = None
    owner_id: str = None
    owner: bool = None
    member_count: int = None
    max_members: int = None
    description: str = None
    joined_at: str = None


class User(BaseModel):
    id: str = None
    username: str = None
    avatar: str = None
    bot: bool = None
    union_openid: str = None
    union_user_account: str = None


class Channel(BaseModel):
    id: str = None
    guild_id: str = None
    name: str = None
    type: int = None
    sub_type: int = None
    position: int = None
    parent_id: str = None
    owner_id: str = None
    private_type: int = None
    speak_permission: int = None
    application_id: str = None


class ChannelCreate(BaseModel):
    name: str
    type: int
    sub_type: int
    position: int = None
    parent_id: str = None
    private_type: int = None
    private_user_ids: List[str] = None


class ChannelUpdate(BaseModel):
    name: str = None
    type: int = None
    sub_type: int = None
    position: int = None
    parent_id: str = None
    private_type: int = None


class Member(BaseModel):
    user: User = None
    nick: str = None
    roles: List[str] = None
    joined_at: str = None


class DeleteMemberBody(BaseModel):
    add_blacklist: bool = None


class Role(BaseModel):
    id: str = None
    name: str = None
    color: int = None
    hoist: int = None
    number: int = None
    member_limit: int = None


class GetGuildRolesReturn(BaseModel):
    guild_id: str = None
    roles: List[Role] = None
    role_num_limit: str = None


class PostGuildRoleBody(BaseModel):
    name: str
    color: float = None
    hoist: float = None


class GuildRole(BaseModel):
    id: str = None
    name: str = None
    color: float = None
    hoist: float = None
    number: float = None
    member_limit: float = None


class PostGuildRoleReturn(BaseModel):
    role_id: str = None
    role: GuildRole = None


class PatchGuildRoleBody(BaseModel):
    name: str = None
    color: float = None
    hoist: float = None


class PatchGuildRoleReturn(BaseModel):
    guild_id: str = None
    role_id: str = None
    role: GuildRole = None


class PutGuildMemberRoleBody(BaseModel):
    id: str = None


class DeleteGuildMemberRoleBody(BaseModel):
    id: str = None


class ChannelPermissions(BaseModel):
    channel_id: str = None
    user_id: str = None
    role_id: str = None
    permissions: str = None


class PutChannelPermissionsBody(BaseModel):
    add: str = None
    remove: str = None


class PutChannelRolesPermissionsBody(BaseModel):
    add: str = None
    remove: str = None


class MessageAttachment(BaseModel):
    url: str = None


class MessageEmbedThumbnail(BaseModel):
    url: str = None


class MessageEmbedField(BaseModel):
    name: str = None


class MessageEmbed(BaseModel):
    title: str = None
    prompt: str = None
    thumbnail: MessageEmbedThumbnail = None
    fields: List[MessageEmbedField] = None


class MessageArkObjKv(BaseModel):
    key: str = None
    value: str = None


class MessageArkObj(BaseModel):
    obj_kv: List[MessageArkObjKv] = None


class MessageArkKv(BaseModel):
    key: str = None
    value: str = None
    obj: List[MessageArkObj] = None


class MessageArk(BaseModel):
    template_id: int = None
    kv: List[MessageArkKv] = None


class MessageReference(BaseModel):
    message_id: str = None
    ignore_get_message_error: bool = None


class Message(BaseModel):
    id: str = None
    channel_id: str = None
    guild_id: str = None
    content: str = None
    timestamp: str = None
    edited_timestamp: str = None
    mention_everyone: bool = None
    author: User = None
    attachments: List[MessageAttachment] = None
    embeds: List[MessageEmbed] = None
    mentions: List[User] = None
    member: Member = None
    ark: MessageArk = None
    seq: int = None
    message_reference: MessageReference = None


class MessageSend(BaseModel):
    content: str = None
    embed: MessageEmbed = None
    ark: MessageArk = None
    message_reference: MessageReference = None
    image: str = None
    msg_id: str = None


class PostDmsBody(BaseModel):
    recipient_id: str
    source_guild_id: str


class DMS(BaseModel):
    guild_id: str = None
    channel_id: str = None
    create_time: str = None


class PatchGuildMuteBody(BaseModel):
    mute_end_timestamp: str = None
    mute_seconds: str = None


class PatchGuildMemberMuteBody(BaseModel):
    mute_end_timestamp: str = None
    mute_seconds: str = None


class PostGuildAnnouncesBody(BaseModel):
    message_id: str
    channel_id: str


class PostChannelAnnouncesBody(BaseModel):
    message_id: str


class Announces(BaseModel):
    guild_id: str = None
    channel_id: str = None
    message_id: str = None


class GetSchedulesBody(BaseModel):
    since: int = None


class Schedule(BaseModel):
    id: str = None
    name: str = None
    description: str = None
    start_timestamp: str = None
    end_timestamp: str = None
    creator: Member = None
    jump_channel_id: str = None
    remind_type: str = None


class ScheduleCreate(BaseModel):
    name: str
    description: str = None
    start_timestamp: str
    end_timestamp: str
    creator: Member = None
    jump_channel_id: str = None
    remind_type: str


class ScheduleUpdate(BaseModel):
    name: str = None
    description: str = None
    start_timestamp: str = None
    end_timestamp: str = None
    creator: Member = None
    jump_channel_id: str = None
    remind_type: str = None


class AudioControl(BaseModel):
    audio_url: str = None
    text: str = None
    status: int = None


class APIPermission(BaseModel):
    path: str = None
    method: str = None
    desc: str = None
    auth_status: int = None


class APIPermissionDemandIdentify(BaseModel):
    path: str = None
    name: str = None


class PostApiPermissionDemandBody(BaseModel):
    channel_id: str = None
    api_identify: APIPermissionDemandIdentify = None
    desc: str = None


class APIPermissionDemand(BaseModel):
    guild_id: str = None
    channel_id: str = None
    api_identify: APIPermissionDemandIdentify = None
    title: str = None
    desc: str = None


class UrlGetReturn(BaseModel):
    url: str = None


class SessionStartLimit(BaseModel):
    total: int = None
    remaining: int = None
    reset_after: int = None
    max_concurrency: int = None


class ShardUrlGetReturn(BaseModel):
    url: str = None
    shards: int = None
    session_start_limit: SessionStartLimit = None


class PinsMessage(BaseModel):
    guild_id: str = None
    channel_id: str = None
    message_ids: List[str] = None
