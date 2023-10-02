from enum import IntEnum
from typing import Tuple, Union
from typing_extensions import Literal, Annotated

from pydantic import Extra, Field, BaseModel

from .transformer import AliasExportTransformer


class Opcode(IntEnum):
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    RESUME = 6
    RECONNECT = 7
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class Payload(AliasExportTransformer, BaseModel):
    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True


class Dispatch(Payload):
    opcode: Literal[Opcode.DISPATCH] = Field(Opcode.DISPATCH, alias="op")
    data: dict = Field(alias="d")
    sequence: int = Field(alias="s")
    type: str = Field(alias="t")


class Heartbeat(Payload):
    opcode: Literal[Opcode.HEARTBEAT] = Field(Opcode.HEARTBEAT, alias="op")
    data: int = Field(alias="d")


class IdentifyData(BaseModel, extra=Extra.allow):
    token: str
    intents: int
    shard: Tuple[int, int]
    properties: dict


class Identify(Payload):
    opcode: Literal[Opcode.IDENTIFY] = Field(Opcode.IDENTIFY, alias="op")
    data: IdentifyData = Field(alias="d")


class ResumeData(BaseModel, extra=Extra.allow):
    token: str
    session_id: str
    seq: int


class Resume(Payload):
    opcode: Literal[Opcode.RESUME] = Field(Opcode.RESUME, alias="op")
    data: ResumeData = Field(alias="d")


class Reconnect(Payload):
    opcode: Literal[Opcode.RECONNECT] = Field(Opcode.RECONNECT, alias="op")


class InvalidSession(Payload):
    opcode: Literal[Opcode.INVALID_SESSION] = Field(Opcode.INVALID_SESSION, alias="op")


class HelloData(BaseModel, extra=Extra.allow):
    heartbeat_interval: int


class Hello(Payload):
    opcode: Literal[Opcode.HELLO] = Field(Opcode.HELLO, alias="op")
    data: HelloData = Field(alias="d")


class HeartbeatAck(Payload):
    opcode: Literal[Opcode.HEARTBEAT_ACK] = Field(Opcode.HEARTBEAT_ACK, alias="op")


PayloadType = Union[
    Annotated[
        Union[Dispatch, Reconnect, InvalidSession, Hello, HeartbeatAck],
        Field(discriminator="opcode"),
    ],
    Payload,
]
