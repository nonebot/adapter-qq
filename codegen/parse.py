import warnings
from urllib.parse import urlparse
from contextvars import ContextVar
from typing import Any, Dict, List, Tuple, Optional

from yarl import URL
from pydantic import parse_obj_as

from .config import Config
from .source import Source
from .model import API, Type, Object, DataType, PathParam, QueryParam, obj_schemas

current_source: ContextVar[Source] = ContextVar("current_source")


def _resolve_ref(obj: DataType, loc: Tuple[str, ...]) -> DataType:
    source = current_source.get()
    if isinstance(obj, dict) and "$ref" in obj:
        ref = URL(obj["$ref"])
        source = source.resolve(ref)
        s_token = current_source.set(source)
        result = _resolve_ref(
            source.resolve_fragment(ref.fragment), (ref.fragment.split("/")[-1],)
        )
        current_source.reset(s_token)
        return result
    elif isinstance(obj, dict):
        is_object_schema = ("type" in obj and obj["type"] == "object") or (
            "properties" in obj and isinstance(obj["properties"], dict)
        )
        new_obj = {"name": "_".join(loc), "type": "object"} if is_object_schema else {}
        for key, value in obj.items():
            new_obj[key] = _resolve_ref(value, loc + (key,))
        return new_obj
    elif isinstance(obj, list):
        new_obj = []
        for index, item in enumerate(obj):
            new_obj.append(_resolve_ref(item, loc + (str(index),)))
        return new_obj
    else:
        return obj


def _schema_to_model(schema: dict, loc: Tuple[str, ...]) -> Type:
    schema = _resolve_ref(schema, loc)
    model = parse_obj_as(Type, schema)
    if isinstance(model, Object):
        obj_schemas[model.name] = model
    return model


def parse(source: Source) -> List[API]:
    apis: List[API] = []
    current_source.set(source)

    schemas = source.data.get("components", {}).get("schemas", {})
    for schema_name, schema in schemas.items():
        _schema_to_model(schema, (schema_name,))

    paths = source.data.get("paths", {}) or {}
    for path, path_item in paths.items():
        path_token = None
        if "$ref" in path_item:
            ref = URL(path_item["$ref"])
            path_source = source.resolve(ref)
            path_token = current_source.set(path_source)
            path_item = path_source.resolve_fragment(ref.fragment)

        common_parameters = path_item.get("parameters", [])

        for method, operation in path_item.items():
            if method not in {
                "get",
                "put",
                "post",
                "delete",
                "options",
                "head",
                "patch",
                "trace",
            }:
                continue

            # get api name from doc url
            doc_url = operation.get("externalDocs", {}).get("url", None)
            if doc_url is None:
                warnings.warn(f"{path} {method} has no external docs")
                continue
            name = (
                urlparse(doc_url)
                .path.split("/")[-1]
                .removesuffix(".html")
                .replace("-", "_")
            )

            # get api params
            path_params: List[PathParam] = []
            query_params: List[QueryParam] = []
            parameters = common_parameters + operation.get("parameters", [])
            for param in parameters:
                param_token = None
                if "$ref" in param:
                    ref = URL(param["$ref"])
                    param_source = source.resolve(ref)
                    param_token = current_source.set(param_source)
                    param = param_source.resolve_fragment(ref.fragment)

                type = param["in"]
                if type == "path":
                    path_params.append(
                        PathParam(
                            name=param["name"],
                            required=param.get("required", False),
                            type=_schema_to_model(
                                param["schema"], (name, param["name"])
                            ),
                        )
                    )
                elif type == "query":
                    query_params.append(
                        QueryParam(
                            name=param["name"],
                            required=param.get("required", False),
                            type=_schema_to_model(
                                param["schema"], (name, param["name"])
                            ),
                        )
                    )
                else:
                    warnings.warn(f"Unsupported param type: {param}")

                if param_token:
                    current_source.reset(param_token)

            # get api body
            body_schema = (
                operation.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", None)
            )
            body = (
                _schema_to_model(body_schema, (name, "body")) if body_schema else None
            )

            # get api return value
            responses = operation.get("responses", {})
            response = responses.get(200, {}) or responses.get("default", {})
            return_schema = (
                response.get("content", {})
                .get("application/json", {})
                .get("schema", None)
            )
            return_type = (
                _schema_to_model(return_schema, (name, "return"))
                if return_schema
                else None
            )

            apis.append(
                API(
                    name=name,
                    method=method,
                    path=path,
                    path_params=path_params,
                    query_params=query_params,
                    body=body,
                    return_type=return_type,
                )
            )

        if path_token:
            current_source.reset(path_token)
    return apis
