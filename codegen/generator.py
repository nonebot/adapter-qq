import re
from typing import List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .model import API, obj_schemas


def generate(config: Config, apis: List[API]):
    env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))
    client_template = env.get_template("client.py.jinja")
    client_output = client_template.render(apis=apis)
    handle_template = env.get_template("handle.py.jinja")
    handle_output = handle_template.render(apis=apis)
    model_template = env.get_template("model.py.jinja")
    model_output = model_template.render(models=obj_schemas.values())
    config.model_output.write_text(model_output)
    config.client_output.write_text(client_output)
    config.handle_output.write_text(handle_output)
