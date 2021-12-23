from pydantic import Field, HttpUrl, BaseModel


class Config(BaseModel):
    is_sandbox: bool = False
    qqguild_api_base: HttpUrl = Field("https://api.sgroup.qq.com/")
    qqguild_sandbox_api_base: HttpUrl = Field("https://sandbox.api.sgroup.qq.com")

    class Config:
        extra = "ignore"
