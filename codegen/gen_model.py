from datamodel_code_generator import generate

from .config import Config


def generate_model(source: str, config: Config) -> None:
    generate(
        source,
        input_filename="openapi.yaml",
        input_file_type=config.input_file_type,
        output=config.output,
        target_python_version=config.target_python_version,
    )
