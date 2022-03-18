from typing import Set, List
from argparse import ArgumentParser

from yarl import URL

from .model import API
from .parse import parse
from .source import Source
from .config import get_config
from .generator import generate

parser = ArgumentParser()

if __name__ == "__main__":
    options = parser.parse_args()
    config = get_config(vars(options))
    apis: List[API] = []
    parsed_source: Set[URL] = set()
    Source.from_source(URL(config.url))
    while remain := set(Source._cache.keys()) - parsed_source:
        source = Source._cache[list(remain)[0]]
        apis.extend(parse(source))
        parsed_source.add(source.source)
    generate(config, apis)
