import sys
from typing import (
    Any,
    Dict,
    Final,
    Generator,
    Generic,
    Iterable,
    List,
    Mapping,
    Optional,
    Protocol,
    TypeVar,
)

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")


class Filter(Protocol, Generic[T]):
    def __call__(self, buffer: List[T], new: T) -> bool:  # type: ignore
        pass


class Converter(Protocol, Generic[T1, T2]):  # type: ignore
    def __call__(self, x: T1) -> T2:  # type: ignore
        pass


class Parser(Generic[T1, T2]):
    filter_fn: Filter[T1]
    post_fn: Converter[List[T1], T2]
    _buffer: List[T1]

    def __init__(self, filter_fn, post_fn=lambda x: x):
        self.filter_fn = filter_fn
        self.post_fn = post_fn
        self._buffer = []

    def flush(self) -> T2:
        flushed = self.post_fn(self._buffer)
        self._buffer = []
        return flushed

    def push_one(self, new: T1) -> Optional[T2]:
        hold_buffer = self.filter_fn(self._buffer, new)
        if hold_buffer:
            return
        return self.flush()

    def is_flushed(self):
        return self._buffer == []


def input_chars() -> Generator[str, None, None]:
    for line in sys.stdin:
        for char in line:
            yield char


DEFAULT_FILTER: Filter = lambda buffer, new: not buffer.append(new)


def dict_filter(
    cases: Mapping[T, Filter[T]], default_filter: Filter[T] = DEFAULT_FILTER
) -> Filter[T]:
    return lambda buffer, new: cases.get(new, default_filter)(buffer, new)


def _cover_list(x: list):
    covered = tuple(x)
    x.clear()
    x.append(covered)
    return True


def push_one_to(parsers: Iterable[Parser], new):
    for parser in parsers:
        new = parser.push_one(new)
        if new is None:
            return


def flush_all(parsers: Iterable[Parser]):
    new = None
    for parser in parsers:
        if new is not None:
            new = parser.push_one(new)
        if not parser.is_flushed():
            new = parser.flush()
    return new


def parsers_processor(parsers: Iterable, inbound: Iterable):
    yield from (push_one_to(parsers, new) for new in inbound)
    yield flush_all(parsers)


def main():
    print("Enter Ctrl + Z and Enter on WIndows or Ctrl + D on UNIX-like to send EOF")

    CHAR_OPS_DICT: Mapping[str, Filter[str]] = {
        " ": lambda buffer, new: False,
        "\n": lambda buffer, new: False,
    }
    POST_SYMBOL: Final[Converter] = lambda x: "".join(x)

    SYMBOLS_DICT: Mapping[str, Filter[str]] = {
        "": lambda buffer, new: True,
        ",": lambda buffer, new: False,
    }
    POST_SYMBOLS_BUFFER: Final[Converter] = lambda x: tuple(x)

    CMDS_DICT: Dict[Any, Filter] = {tuple(): lambda buffer, new: _cover_list(buffer)}

    chars_parser = Parser(dict_filter(CHAR_OPS_DICT), POST_SYMBOL)
    symbols_parser = Parser(dict_filter(SYMBOLS_DICT), POST_SYMBOLS_BUFFER)
    cmds_parser = Parser(dict_filter(CMDS_DICT))
    parsers = [chars_parser, symbols_parser, cmds_parser]
    for _ in parsers_processor(parsers, input_chars()):
        buffer = _
    print(buffer)


if __name__ == "__main__":
    main()
