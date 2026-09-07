from datetime import datetime, time, timedelta, timezone
from typing import Literal, TypeAlias
from urllib.parse import urlparse

from nonebot.compat import field_validator
from pydantic import BaseModel, Field


class FriendAuthor(BaseModel):
    id: str
    user_openid: str
    union_openid: str | None = None
    username: str | None = None


class GroupMemberAuthor(BaseModel):
    id: str
    bot: bool
    member_openid: str
    member_role: Literal["member", "admin", "owner"]
    union_openid: str | None = None
    username: str | None = None


class GroupMentionUser(BaseModel):
    scope: Literal["single"]
    bot: bool
    id: str
    is_you: bool
    member_openid: str
    username: str


class GroupMentionEveryone(BaseModel):
    scope: Literal["all"]
    is_you: Literal[True]
    username: str


GroupMention: TypeAlias = GroupMentionUser | GroupMentionEveryone


class Attachment(BaseModel):
    content_type: str
    filename: str | None = None
    height: int | None = None
    width: int | None = None
    size: int | None = None
    url: str | None = None

    @field_validator("url", mode="after")
    def check_url(cls, v: str):
        if v and not urlparse(v).hostname:
            return f"https://{v}"
        return v


class Media(BaseModel):
    file_info: str


class _QQMessageScene(BaseModel):
    ext: list[str]
    source: str


class _ReplyAuthor(BaseModel):
    id: str | None = None
    bot: bool = False
    username: str | None = None
    union_openid: str | None = None
    union_user_account: str | None = None
    user_openid: str | None = None
    member_openid: str | None = None


class QQReplyMessage(BaseModel):
    content: str
    attachments: list[Attachment] | None = None
    message_type: int | None = None
    msg_idx: str | None = None
    author: _ReplyAuthor | None = None


class QQMessage(BaseModel):
    id: str
    content: str
    timestamp: str
    mentions: list[GroupMention] | None = None
    attachments: list[Attachment] | None = None
    message_scene: _QQMessageScene | None = None
    message_type: int | None = None
    msg_idx: str | None = None
    msg_elements: list[QQReplyMessage] | None = None


class UserQQMessage(QQMessage):
    author: FriendAuthor


class GroupQQMessage(QQMessage):
    author: GroupMemberAuthor


class PostC2CMessagesReturn(BaseModel):
    id: str | None = None
    timestamp: datetime | None = None


class PostGroupMessagesReturn(BaseModel):
    id: str | None = None
    timestamp: datetime | None = None


class PostC2CFilesReturn(BaseModel):
    file_uuid: str | None = None
    file_info: str | None = None
    ttl: int | None = None


class UploadPartItem(BaseModel):
    index: int
    presigned_url: str


class UploadConfig(BaseModel):
    concurrency: int
    retry_timeout: int
    retry_delay: int


class PostC2CFilesPrepareReturn(BaseModel):
    upload_id: str
    block_size: int
    parts: list[UploadPartItem]
    upload_config: UploadConfig


class PostGroupFilesReturn(BaseModel):
    file_uuid: str | None = None
    file_info: str | None = None
    ttl: int | None = None


class PostGroupFilesPrepareReturn(BaseModel):
    upload_id: str
    block_size: int
    parts: list[UploadPartItem]
    upload_config: UploadConfig


class GroupMember(BaseModel):
    member_openid: str
    join_timestamp: datetime


class PostGroupMembersReturn(BaseModel):
    members: list[GroupMember]
    next_index: int | None = None


class GroupInfoReturn(BaseModel):
    group_openid: str
    group_name: str
    group_finger_memo: str
    group_class_text: str
    group_tags: list[str]
    group_member_num: int


class GroupBotStateReturn(BaseModel):
    member_openid: str
    joined_at: datetime
    allow_proactive_msg: bool
    recv_msg_setting: Literal["all", "only_mention", "mention_and_context"]
    member_role: Literal["member", "owner", "admin"]


class MemberMuteState(BaseModel):
    member_openid: str
    mute_expire_at: datetime
    username: str
    union_openid: str | None = None


class MuteScheduleRule(BaseModel):
    task_id: str
    start_at: datetime
    end_at: datetime
    enabled: bool


class MuteRecurringRule(BaseModel):
    task_id: str
    weekdays: list[int]
    start_time: time
    end_time: time
    enabled: bool


class GlobalMuteRule(BaseModel):
    mode: Literal["none", "always", "schedule"]
    schedule_rules: list[MuteScheduleRule]
    recurring_rules: list[MuteRecurringRule]


class GroupRestrictChatSettingReturn(BaseModel):
    global_rule: GlobalMuteRule
    members: list[MemberMuteState]


class SetMemberMuteState(BaseModel):
    op: Literal["add", "update", "del"]
    member_openid: str
    mute_expire_at: str | datetime | timedelta | None = None

    @field_validator("mute_expire_at", mode="before")
    @classmethod
    def normalize_expire(cls, v):
        if isinstance(v, timedelta):
            return (datetime.now(timezone.utc) + v).astimezone().isoformat()
        if isinstance(v, datetime):
            if v.tzinfo is None:
                v = v.astimezone()
            return v.isoformat()
        return v


class ReviewQA(BaseModel):
    question: str
    answer: str


class VerifyInfo(BaseModel):
    method: str
    verify_message: str | None = None
    review_qa_list: list[ReviewQA] | None = None


class JoinRequest(BaseModel):
    join_request_id: str
    risk_tips: str | None = None
    union_openid: str | None = None
    member_openid: str
    username: str
    apply_at: datetime
    apply_source: Literal["self_apply", "invited"]
    invited_by: str | None = None
    bot: bool = False
    verify_info: VerifyInfo | None = None


class JoinRequestListReturn(BaseModel):
    list: list[JoinRequest]
    next_cursor: str


class AutoApproved(BaseModel):
    strategy_id: str


class MessageActionButton(BaseModel):
    template_id: Literal["1", "10"] = "1"  # 待废弃字段！！！
    callback_data: str | None = None
    feedback: bool | None = None  # 反馈按钮（赞踩按钮）
    tts: bool | None = None  # TTS 语音播放按钮
    re_generate: bool | None = None  # 重新生成按钮
    stop_generate: bool | None = None  # 停止生成按钮


class PromptAction(BaseModel):
    type: Literal[2] = 2


class PromptRenderData(BaseModel):
    label: str
    style: Literal[2] = 2


class PromptButton(BaseModel):
    render_data: PromptRenderData
    action: PromptAction


class PromptRow(BaseModel):
    buttons: list[PromptButton]


class PromptContent(BaseModel):
    rows: list[PromptRow]


class PromptKeyboardModel(BaseModel):
    content: PromptContent


class MessagePromptKeyboard(BaseModel):
    keyboard: PromptKeyboardModel


class MessageStream(BaseModel):
    state: Literal[1, 10, 11, 20]
    """1: 正文生成中, 10: 正文生成结束, 11: 引志消息生成中, 20: 引导消息生成结束。"""
    id: str | None = None
    """第一条不用填写，第二条需要填写第一个分片返回的 msgID"""
    index: int
    """从 1 开始"""
    reset: bool | None = None
    """只能用于流式消息没有发送完成时，reset 时 index 需要从 0 开始，需要填写流式 id"""


class GroupMemberInfo(BaseModel):
    member_openid: str
    username: str | None = None
    member_role: Literal["member", "owner", "admin"] | None = None
    bot: bool
    joined_at: datetime | None = None
    union_openid: str | None = None


class GroupMembersReturn(BaseModel):
    members: list[GroupMemberInfo]
    next_cursor: str | None = None


class BatchRemoveMembersReturn(BaseModel):
    remove_members_result: str | None = None
    add_to_member_blacklist_fail_openids: list[str] = Field(default_factory=list)


class BlacklistUser(BaseModel):
    union_openid: str | None = None
    member_openid: str
    username: str | None = None
    banned_at: datetime | None = None
    bot: bool


class GroupMemberBlacklistReturn(BaseModel):
    users: list[BlacklistUser]
    next_cursor: str | None = None


class MemberBlacklistOpReturn(BaseModel):
    fail_openids: list[str] = Field(default_factory=list)


__all__ = [
    "Attachment",
    "AutoApproved",
    "BatchRemoveMembersReturn",
    "BlacklistUser",
    "FriendAuthor",
    "GlobalMuteRule",
    "GroupBotStateReturn",
    "GroupInfoReturn",
    "GroupMember",
    "GroupMemberAuthor",
    "GroupMemberBlacklistReturn",
    "GroupMemberInfo",
    "GroupMembersReturn",
    "GroupMention",
    "GroupMentionEveryone",
    "GroupMentionUser",
    "GroupQQMessage",
    "GroupRestrictChatSettingReturn",
    "JoinRequest",
    "JoinRequestListReturn",
    "Media",
    "MemberBlacklistOpReturn",
    "MemberMuteState",
    "MessageActionButton",
    "MessagePromptKeyboard",
    "MessageStream",
    "MuteRecurringRule",
    "MuteScheduleRule",
    "PostC2CFilesPrepareReturn",
    "PostC2CFilesReturn",
    "PostC2CMessagesReturn",
    "PostGroupFilesPrepareReturn",
    "PostGroupFilesReturn",
    "PostGroupMembersReturn",
    "PostGroupMessagesReturn",
    "PromptAction",
    "PromptButton",
    "PromptContent",
    "PromptKeyboardModel",
    "PromptRenderData",
    "PromptRow",
    "QQMessage",
    "QQReplyMessage",
    "ReviewQA",
    "SetMemberMuteState",
    "UserQQMessage",
    "VerifyInfo",
]
