import re
from enum import Enum
from typing import Any, Dict, List, Union, Literal, Optional, Annotated

from pydantic import Field, BaseModel

DataType = Any


obj_schemas: Dict[str, "Object"] = {}


def snake_to_pascal(snake: str) -> str:
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), snake)


class TypeEnum(str, Enum):
    array = "array"
    boolean = "boolean"
    integer = "integer"
    number = "number"
    object = "object"
    string = "string"


class Array(BaseModel):
    type: Literal[TypeEnum.array]
    items: "Type"

    def to_annotation(self):
        return f"List[{self.items.to_annotation()}]"


class Boolean(BaseModel):
    type: Literal[TypeEnum.boolean]

    def to_annotation(self):
        return "bool"


class Integer(BaseModel):
    type: Literal[TypeEnum.integer]

    def to_annotation(self):
        return "int"


class Number(BaseModel):
    type: Literal[TypeEnum.number]

    def to_annotation(self):
        return "float"


class Object(BaseModel):
    name: str
    type: Literal[TypeEnum.object] = Field(TypeEnum.object)
    properties: Dict[str, "Type"]
    required: List[str] = Field(default_factory=list)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        obj_schemas[self.name] = self

    def to_annotation(self):
        return snake_to_pascal(self.name)

    def property_annotation(self, name: str):
        annotation = self.properties[name].to_annotation()
        if name not in self.required:
            annotation = f"Optional[{annotation}]"
        return annotation


class String(BaseModel):
    type: Literal[TypeEnum.string]

    def to_annotation(self):
        return "str"


Type = Annotated[
    Union[Array, Boolean, Integer, Number, Object, String], Field(discriminator="type")
]


class PathParam(BaseModel):
    name: str
    required: bool = False
    type: Type

    def to_annotation(self):
        annotation = self.type.to_annotation()
        if not self.required:
            annotation = f"Optional[{annotation}]"
        return annotation


class QueryParam(BaseModel):
    name: str
    required: bool = False
    type: Type

    def to_annotation(self):
        annotation = self.type.to_annotation()
        if not self.required:
            annotation = f"Optional[{annotation}]"
        return annotation


class API(BaseModel):
    name: str
    method: str
    path: str
    path_params: List[PathParam]
    query_params: List[QueryParam]
    body: Optional[Type]
    return_type: Optional[Type]


Array.update_forward_refs()
Object.update_forward_refs()
