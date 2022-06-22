import logging
import re
from dataclasses import dataclass
from typing import Protocol, List

from nltk.tokenize import wordpunct_tokenize  # type:ignore
from nltk.util import ngrams  # type:ignore

LOGGER = logging.getLogger(__name__)


class CharFilter(Protocol):
    def filter(self, event: str) -> str:
        ...


class Tokenizer(Protocol):
    def tokenize(self, event: str) -> List[str]:
        ...


class TokenFilter(Protocol):
    def filter(self, tokens: List[str]) -> List[str]:
        ...


class LowerCasingFilter:
    @staticmethod
    def filter(event: str) -> str:
        return event.lower()


class SimpleTokenizer:
    @staticmethod
    def tokenize(event: str) -> List[str]:
        tokens = wordpunct_tokenize(event)
        return tokens


class NgramTokenStreamEnricher:
    def __init__(self, ns: List[int]):
        self.__ns = ns

    def filter(self, tokens: List[str]) -> List[str]:
        result = tokens.copy()
        for current_ngram in self.__ns:
            for i in range(0, len(tokens) - current_ngram + 1):
                format_string = "##___##".join(["%s" for _ in range(current_ngram)])
                token = format_string % tuple(tokens[i:i + current_ngram])
                result.append(token)
        return result


class NumericTokenFilter:
    def __init__(self):
        self.__numeric_pattern = re.compile('^\\d+$')

    def filter(self, tokens: List[str]) -> List[str]:
        return [x for x in tokens if not self.__numeric_pattern.match(x)]


class SingleCharTokenFilter:
    @staticmethod
    def filter(tokens: List[str]) -> List[str]:
        return [x for x in tokens if len(x) > 1 or x.isalpha()]


@dataclass
class Analyzer:
    """
    Inspired by ElasticSearch analyzer:
    https://www.elastic.co/guide/en/elasticsearch/reference/current/analyzer-anatomy.html
    """
    char_filters: List[CharFilter]
    tokenizer: Tokenizer
    token_filters: List[TokenFilter]

    def analyze(self, event: str) -> List[str]:
        current_event = event

        # Character filtering (str -> str)
        for char_filter in self.char_filters:
            current_event = char_filter.filter(current_event)

        # Tokenization (str -> str[])
        tokens = self.tokenizer.tokenize(current_event)

        # Token filtering (str[] -> str[])
        for token_filter in self.token_filters:
            tokens = token_filter.filter(tokens)
        LOGGER.debug(f"EVENT={event} TOKENS={tokens}")
        return tokens


DEFAULT_ANALYZER = Analyzer([LowerCasingFilter()], SimpleTokenizer(), [NumericTokenFilter(), SingleCharTokenFilter()])
