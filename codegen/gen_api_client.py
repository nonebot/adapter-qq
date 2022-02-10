import warnings
from typing import List
from pathlib import Path
from textwrap import indent
from urllib.parse import urlparse

from yaml import SafeLoader, load

from .config import Config

TEMPLATE = """
from typing import TYPE_CHECKING

from pydantic import Extra, BaseModel

from .model import *

{types}

if TYPE_CHECKING:

{defenitions}

else:

    class ApiClient:
        ...

""".strip()

TYPES_MAP = {"string": "str", "integer": "int", "boolean": "bool", "number": "int"}


def generate_object(
    name: str, schema: dict, types: List[str], definitions: List[str]
) -> str:
    temp = []
    temp.append(f"class {name}(BaseModel, extra=Extra.allow):")
    required = schema.get("required", [])
    for property_name, property in schema.get("properties", {}).items():
        property_type = generate_type(
            f"{name}_{property_name}", property, types, definitions
        )
        property_str = f"{property_name}: "

        if property_name not in required:
            property_str += f"Optional[{property_type}] = None"
        else:
            property_str += f"{property_type}"

        temp.append(indent(property_str, " " * 4))

    types.extend(temp)
    return name


def generate_type(
    name: str, schema: dict, types: List[str], definitions: List[str]
) -> str:
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    elif not schema:
        return "None"

    type: str = schema.get("type", "object")
    if type == "object":
        return generate_object(name, schema, types, definitions)
    elif type in TYPES_MAP:
        return TYPES_MAP[type]
    elif type == "array":
        return f"List[{generate_type(name, schema['items'], types, definitions)}]"
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
            method_str = indent(f"async def {name}(self, ", " " * 4)

            parameters = operation.get("parameters", [])
            if parameters:
                method_str += "*, "
            for param in parameters:
                param_name = param["name"]
                param_type = generate_type(
                    f"{name}_param_{param_name}", param["schema"], types, definitions
                )
                method_str += f"{param_name}: {param_type}"

                required = param.get("required", False)
                if not required:
                    method_str += "=..."

                method_str += ", "

            request_body = operation.get("requestBody", {})
            schema = (
                request_body.get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            if "$ref" in schema:
                schema = (
                    content.get("components", {})
                    .get("schemas", {})
                    .get(schema["$ref"].split("/")[-1])
                )
            if schema:
                required = schema.get("required", [])
                for property_name, property in schema.get("properties", {}).items():
                    property_type = generate_type(
                        f"{name}_body_{property_name}", property, types, definitions
                    )
                    method_str += f"{property_name}: {property_type}"

                    if property_name not in required:
                        method_str += " = ..."

                    method_str += ", "

            method_str = method_str.removesuffix(", ")
            method_str += ")"

            responses = operation.get("responses", {})
            response = responses.get(200, {}) or responses.get("default", {})
            return_schema = (
                response.get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            method_str += f" -> {generate_type(f'{name}_return', return_schema, types, definitions)}"

            method_str += ": ..."
            definitions.append(method_str)

    definition = indent("\n".join(definitions), " " * 4)
    type = "\n".join(types)
    generated = TEMPLATE.format(types=type, defenitions=definition)
    output_file = Path(config.client_output)
    with output_file.open("w", encoding="utf-8") as f:
        f.write(generated)
