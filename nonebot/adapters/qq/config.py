from typing import List, Tuple, Optional

from pydantic import Extra, Field, HttpUrl, BaseModel


class Intents(BaseModel):
    guilds: bool = True
    guild_members: bool = True
    guild_messages: bool = False
    guild_message_reactions: bool = True
    direct_message: bool = False
    open_forum_event: bool = False
    audio_live_member: bool = False
    c2c_group_at_messages: bool = False
    interaction: bool = False
    message_audit: bool = True
    forum_event: bool = False
    audio_action: bool = False
    at_messages: bool = True

    def to_int(self):
        return (
            self.guilds << 0
            | self.guild_members << 1
            | self.guild_messages << 9
            | self.guild_message_reactions << 10
            | self.direct_message << 12
            | self.open_forum_event << 18
            | self.audio_live_member << 19
            | self.c2c_group_at_messages << 25
            | self.interaction << 26
            | self.message_audit << 27
            | self.forum_event << 28
            | self.audio_action << 29
            | self.at_messages << 30
        )

    @property
    def is_group_enabled(self) -> bool:
        """是否开启群聊功能"""
        return self.c2c_group_at_messages is True


class BotInfo(BaseModel):
    id: str = Field(alias="id")
    token: str = Field(alias="token")
    secret: str = Field(alias="secret")
    shard: Optional[Tuple[int, int]] = None
    intent: Intents = Field(default_factory=Intents)

    @property
    def is_group_bot(self) -> bool:
        """是否为群机器人"""
        return self.intent.is_group_enabled


class Config(BaseModel, extra=Extra.ignore):
    qq_is_sandbox: bool = False
    qq_api_base: HttpUrl = Field("https://api.sgroup.qq.com/")
    qq_sandbox_api_base: HttpUrl = Field("https://sandbox.api.sgroup.qq.com")
    qq_auth_base: HttpUrl = Field("https://bots.qq.com/app/getAppAccessToken")
    qq_bots: List[BotInfo] = Field(default_factory=list)
