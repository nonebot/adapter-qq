from enum import IntEnum
from typing import Annotated, Optional, Union
from typing_extensions import Literal

from pydantic import BaseModel, Field

from nonebot.compat import PYDANTIC_V2, ConfigDict

PAYLOAD_FIELD_ALIASES = {"opcode": "op", "data": "d", "sequence": "s", "type": "t"}


class Opcode(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    RESUME = 6
    RECONNECT = 7
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11
    HTTP_CALLBACK_ACK = 12
    WEBHOOK_VERIFY = 13


class Payload(BaseModel):
    if PYDANTIC_V2:
        model_config: ConfigDict = ConfigDict(
            extra="allow",
            populate_by_name=True,
            alias_generator=lambda x: PAYLOAD_FIELD_ALIASES.get(x, x),
        )
    else:

        class Config:
            extra = "allow"
            allow_population_by_field_name = True

            @classmethod
            def alias_generator(cls, string: str) -> str:
                return PAYLOAD_FIELD_ALIASES.get(string, string)


class Dispatch(Payload):
    opcode: Literal[Opcode.DISPATCH] = Field(Opcode.DISPATCH)
    data: dict
    sequence: Optional[int] = None
    type: str
    id: Optional[str] = None


class Heartbeat(Payload):
    opcode: Literal[Opcode.HEARTBEAT] = Field(Opcode.HEARTBEAT)
    data: int


class IdentifyData(BaseModel):
    token: str
    intents: int
    shard: tuple[int, int]
    properties: dict

    if PYDANTIC_V2:
        model_config: ConfigDict = ConfigDict(extra="allow")
    else:

        class Config:
            extra = "allow"


class Identify(Payload):
    opcode: Literal[Opcode.IDENTIFY] = Field(Opcode.IDENTIFY)
    data: IdentifyData


class ResumeData(BaseModel):
    token: str
    session_id: str
    seq: int

    if PYDANTIC_V2:
        model_config: ConfigDict = ConfigDict(extra="allow")
    else:

        class Config:
            extra = "allow"


class Resume(Payload):
    opcode: Literal[Opcode.RESUME] = Field(Opcode.RESUME)
    data: ResumeData


class Reconnect(Payload):
    opcode: Literal[Opcode.RECONNECT] = Field(Opcode.RECONNECT)


class InvalidSession(Payload):
    opcode: Literal[Opcode.INVALID_SESSION] = Field(Opcode.INVALID_SESSION)


class HelloData(BaseModel):
    heartbeat_interval: int

    if PYDANTIC_V2:
        model_config: ConfigDict = ConfigDict(extra="allow")
    else:

        class Config:
            extra = "allow"


class Hello(Payload):
    opcode: Literal[Opcode.HELLO] = Field(Opcode.HELLO)
    data: HelloData


class HeartbeatAck(Payload):
    opcode: Literal[Opcode.HEARTBEAT_ACK] = Field(Opcode.HEARTBEAT_ACK)


class HTTPCallbackAck(Payload):
    opcode: Literal[Opcode.HTTP_CALLBACK_ACK] = Field(Opcode.HTTP_CALLBACK_ACK)
    data: int


class WebhookVerifyData(BaseModel):
    plain_token: str
    event_ts: str

    if PYDANTIC_V2:
        model_config: ConfigDict = ConfigDict(extra="allow")
    else:

        class Config:
            extra = "allow"


class WebhookVerify(Payload):
    opcode: Literal[Opcode.WEBHOOK_VERIFY] = Field(Opcode.WEBHOOK_VERIFY)
    data: WebhookVerifyData


PayloadType = Union[
    Annotated[
        Union[Dispatch, Reconnect, InvalidSession, Hello, HeartbeatAck, WebhookVerify],
        Field(discriminator="opcode"),
    ],
    Payload,
]
