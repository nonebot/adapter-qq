from .config import get_config
from .get_source import get_source
from .gen_model import generate_model
from .gen_api_client import generate_api_client

if __name__ == "__main__":
    config = get_config()
    source = get_source(config)
    generate_model(source, config)
    generate_api_client(source, config)
