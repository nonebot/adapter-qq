from pathlib import Path
from typing import Dict, List

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .model import API, Type, Array, Object, obj_schemas


def sort_models(schemas: Dict[str, Type]) -> Dict[str, Object]:
    models: Dict[str, Object] = {}

    for model in schemas.values():
        if isinstance(model, Array):
            model = model.items

        if not isinstance(model, Object):
            continue

        if model.name in models:
            continue

        models.update(sort_models(model.properties))

        models[model.name] = model

    return models


def generate(config: Config, apis: List[API]):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))
    client_template = env.get_template("client.py.jinja")
    client_output = client_template.render(apis=apis)
    handle_template = env.get_template("handle.py.jinja")
    handle_output = handle_template.render(apis=apis)
    model_template = env.get_template("model.py.jinja")
    model_output = model_template.render(models=sort_models(obj_schemas).values())  # type: ignore
    config.model_output.write_text(model_output)
    config.client_output.write_text(client_output)
    config.handle_output.write_text(handle_output)
