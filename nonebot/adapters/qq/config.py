from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from nonebot.compat import PYDANTIC_V2, ConfigDict


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

    if PYDANTIC_V2:
        model_config: ConfigDict = ConfigDict(extra="forbid")
    else:

        class Config:
            extra = "forbid"

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


class BotInfo(BaseModel):
    id: str = Field(alias="id")
    token: str = Field(alias="token")
    secret: str = Field(alias="secret")
    shard: Optional[tuple[int, int]] = None
    intent: Intents = Field(default_factory=Intents)
    use_websocket: bool = True


class Config(BaseModel):
    qq_is_sandbox: bool = False
    qq_api_base: HttpUrl = Field("https://api.sgroup.qq.com/")  # type: ignore
    qq_sandbox_api_base: HttpUrl = Field("https://sandbox.api.sgroup.qq.com")  # type: ignore
    qq_auth_base: HttpUrl = Field("https://bots.qq.com/app/getAppAccessToken")  # type: ignore
    qq_verify_webhook: bool = True
    qq_bots: list[BotInfo] = Field(default_factory=list)
