from typing import List, NamedTuple

from pydantic import Field, HttpUrl, BaseModel


class BotInfo(NamedTuple):
    app_id: str
    app_token: str
    app_secret: str


class Config(BaseModel):
    qqguild_is_sandbox: bool = False
    qqguild_api_base: HttpUrl = Field("https://api.sgroup.qq.com/")
    qqguild_sandbox_api_base: HttpUrl = Field("https://sandbox.api.sgroup.qq.com")
    qqguild_bots: List[BotInfo] = Field(default_factory=list)

    class Config:
        extra = "ignore"
