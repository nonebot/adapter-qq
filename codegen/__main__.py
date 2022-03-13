from argparse import ArgumentParser

from yarl import URL

from .parse import parse
from .source import Source
from .config import get_config
from .generator import generate

parser = ArgumentParser()

if __name__ == "__main__":
    options = parser.parse_args()
    config = get_config(vars(options))
    source = Source.from_source(URL(config.url))
    apis = parse(source)
    generate(config, apis)
