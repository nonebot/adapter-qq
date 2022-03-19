from typing import List, Tuple, Optional

from pydantic import Field, HttpUrl, BaseModel


class Intents(BaseModel):
    guilds: bool = True
    guild_members: bool = True
    guild_messages: bool = False
    guild_message_reactions: bool = True
    direct_message: bool = False
    message_audit: bool = False
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
            | self.message_audit << 27
            | self.forum_event << 28
            | self.audio_action << 29
            | self.at_messages << 30
        )


class BotInfo(BaseModel):
    id: str = Field(alias="id")
    token: str = Field(alias="token")
    secret: str = Field(alias="secret")
    shard: Optional[Tuple[int, int]] = None
    intent: Intents = Field(default_factory=Intents)


class Config(BaseModel):
    qqguild_is_sandbox: bool = False
    qqguild_api_base: HttpUrl = Field("https://api.sgroup.qq.com/")
    qqguild_sandbox_api_base: HttpUrl = Field("https://sandbox.api.sgroup.qq.com")
    qqguild_bots: List[BotInfo] = Field(default_factory=list)

    class Config:
        extra = "ignore"
