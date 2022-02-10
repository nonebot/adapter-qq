import warnings
from pathlib import Path
from textwrap import indent
from typing import Dict, List
from urllib.parse import urlparse

from yaml import SafeLoader, load

from .config import Config
from .gen_api_client import TYPES_MAP

TEMPLATE = """
from typing import TYPE_CHECKING

from nonebot.drivers import Request
from pydantic.json import pydantic_encoder

from .request import _request

if TYPE_CHECKING:
    from nonebot.adapters.qqguild.bot import Bot
    from nonebot.adapters.qqguild.adapter import Adapter


{defenitions}
"""


def generate_request(source: str, config: Config) -> None:
    definitions: List[str] = []
    handlers: Dict[str, str] = {}

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
            method_str = f'async def _{name}(adapter: "Adapter", bot: "Bot", '
            handlers[name] = f"_{name}"

            parameters = operation.get("parameters", [])
            has_query = False
            if parameters:
                method_str += "*, "
            for param in parameters:
                param_name = param["name"]
                method_str += f"{param_name}: {TYPES_MAP[param['schema']['type']]}"

                required = param.get("required", False)
                if not required:
                    method_str += " = None"

                in_ = param.get("in", "path")
                if in_ == "query":
                    has_query = True

                method_str += ", "

            request_body = operation.get("requestBody", {})
            has_body = False
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
                method_str += "**data"
                has_body = True

            method_str = method_str.removesuffix(", ")
            method_str += "):"

            definitions.append(method_str)

            definitions.append(
                indent(
                    f"request = Request(\n"
                    f'    "{method.upper()}",\n'
                    f'    adapter.get_api_base() / "{path}",\n'
                    f'    headers={{"Authorization": adapter.get_authorization(bot.bot_info)}},\n'
                    f")\n"
                    f"return await _request(adapter, bot, request)",
                    " " * 4,
                )
            )

    definition = "\n".join(definitions)
    generated = TEMPLATE.format(defenitions=definition)
    output_file = Path(config.handle_output)
    with output_file.open("w", encoding="utf-8") as f:
        f.write(generated)
