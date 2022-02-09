import warnings
from typing import List
from textwrap import indent
from urllib.parse import urlparse

from yaml import SafeLoader, load

from .config import Config

TEMPLATE = """
from typing import TYPE_CHECKING
from typing_extensions import TypedDict

if TYPE_CHECKING:

{types}

{defenition}

else:

    class ApiClient:
        ...

""".strip()

TYPES_MAP = {"string": "str", "integer": "int", "boolean": "bool", "number": "int"}


def generate_object(
    name: str, schema: dict, types: List[str], definitions: List[str]
) -> str:
    temp = []
    temp.append(f"class {name}(TypedDict):")
    for property_name, property in schema.get("properties", {}).items():
        property_type = generate_type(
            f"{name}_{property_name}", property, types, definitions
        )
        temp.append(indent(f"{property_name}: {property_type}", " " * 4))

    types.extend(temp)
    return name


def generate_type(
    name: str, schema: dict, types: List[str], definitions: List[str]
) -> str:
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    elif not schema:
        return "None"

    type: str = schema.get("type", None)
    if type == "object":
        return generate_object(name, schema, types, definitions)
    elif type in TYPES_MAP:
        return TYPES_MAP[type]
    else:
        raise ValueError(f"Unknown type {type}, schema: {schema}")


def generate_api_client(source: str, config: Config) -> None:
    types: List[str] = []
    definitions: List[str] = ["class ApiClient:"]

    content = load(source, SafeLoader)
    paths = content.get("paths", {})
    for path, methods in paths.items():
        for method, operation in methods.items():
            doc_path = operation.get("externalDocs", {}).get("url", None)
            if doc_path is None:
                warnings.warn(f"{path} {method} has no external docs")
                continue
            name = (
                urlparse(doc_path)
                .path.split("/")[-1]
                .removesuffix(".html")
                .replace("-", "_")
            )
            method_str = indent(f"def _{name}(self, *, ", " " * 4)

            parameters = operation.get("parameters", [])
            for param in parameters:
                param_name = param["name"]
                param_type = param["type"]
                method_str += f"{param_name}: {TYPES_MAP[param_type]}"

                required = param.get("required", False)
                if not required:
                    method_str += "=..."

                method_str += ", "

            method_str += ")"

            responses = operation.get("responses", {})
            response = responses.get(200, {}) or responses.get("default", {})
            return_schema = (
                response.get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            method_str += (
                f" -> {generate_type(name, return_schema, types, definitions)}"
            )

            method_str += ": ..."
            definitions.append(method_str)
