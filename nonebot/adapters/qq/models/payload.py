from enum import IntEnum
from typing import Tuple, Union
from typing_extensions import Literal, Annotated

from pydantic import Extra, Field, BaseModel

from ._transformer import BoolToIntTransformer, AliasExportTransformer

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


class Payload(AliasExportTransformer, BaseModel):
    class Config:
        extra = Extra.allow
        allow_population_by_field_name = True

        @classmethod
        def alias_generator(cls, string: str) -> str:
            return PAYLOAD_FIELD_ALIASES.get(string, string)


class Dispatch(Payload):
    opcode: Literal[Opcode.DISPATCH] = Field(Opcode.DISPATCH)
    data: dict
    sequence: int
    type: str


class Heartbeat(Payload):
    opcode: Literal[Opcode.HEARTBEAT] = Field(Opcode.HEARTBEAT)
    data: int


class IdentifyData(BaseModel, extra=Extra.allow):
    token: str
    intents: int
    shard: Tuple[int, int]
    properties: dict


class Identify(Payload):
    opcode: Literal[Opcode.IDENTIFY] = Field(Opcode.IDENTIFY)
    data: IdentifyData


class ResumeData(BaseModel, extra=Extra.allow):
    token: str
    session_id: str
    seq: int


class Resume(Payload):
    opcode: Literal[Opcode.RESUME] = Field(Opcode.RESUME)
    data: ResumeData


class Reconnect(Payload):
    opcode: Literal[Opcode.RECONNECT] = Field(Opcode.RECONNECT)


class InvalidSession(Payload):
    opcode: Literal[Opcode.INVALID_SESSION] = Field(Opcode.INVALID_SESSION)


class HelloData(BaseModel, extra=Extra.allow):
    heartbeat_interval: int


class Hello(Payload):
    opcode: Literal[Opcode.HELLO] = Field(Opcode.HELLO)
    data: HelloData


class HeartbeatAck(Payload):
    opcode: Literal[Opcode.HEARTBEAT_ACK] = Field(Opcode.HEARTBEAT_ACK)


class HTTPCallbackAck(BoolToIntTransformer, Payload):
    opcode: Literal[Opcode.HTTP_CALLBACK_ACK] = Field(Opcode.HTTP_CALLBACK_ACK)
    data: bool


PayloadType = Union[
    Annotated[
        Union[Dispatch, Reconnect, InvalidSession, Hello, HeartbeatAck],
        Field(discriminator="opcode"),
    ],
    Payload,
]
