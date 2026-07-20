import sys
from typing import Any, Dict, Final, Generic, List, Mapping, Optional, Protocol, TypeVar

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")

def _cover_list(x: list):
    covered = tuple(x)
    x.clear()
    x.append(covered)
    return True


class Filter(Protocol, Generic[T]):
    def __call__(self, buffer: List[T], new: T) -> bool: # type: ignore
        pass


class Converter(Protocol, Generic[T1, T2]):
    def __call__(self, x: T1) -> T2: # type: ignore
        pass


CHAR_OPS_DICT: Mapping = {
    " ": lambda buffer, new: False,
    "\n": lambda buffer, new: False,
}

SYMBOLS_DICT = {"": lambda buffer, new: True, ",": lambda buffer, new: False}

CMDS_DICT: Dict[Any, Filter[Any]] = {
    tuple(): lambda buffer, new: _cover_list(buffer)
}

DEFAULT_FILTER: Filter = lambda buffer, new: not buffer.append(new)

print("Enter Ctrl + Z and Enter on WIndows or Ctrl + D on UNIX-like to send EOF")
symbol: list = []
POST_SYMBOL: Final[Converter] = lambda x: "".join(x)
symbols_buffer: list = []
POST_SYMBOLS_BUFFER: Final[Converter] = lambda x: tuple(x)
ast: list = []


def dict_filter(cases: Dict[T, Filter[T]], default_filter: Filter[T]) -> Filter[T]:
    return lambda buffer, new: cases.get(new, default_filter)(buffer, new)

def process_buffer(
        buffer: List[T1], 
        new: T1, 
        filter_fn: Filter[T1], 
        post: Converter[List[T1], T2], 
        forced_flush: bool = False) -> Optional[T2]:
    hold_buffer = filter_fn(buffer, new)
    if hold_buffer and not forced_flush:
        return
    flushed = post(buffer)
    buffer.clear()
    return flushed

def process_buffers(buffers, filters, posts, new, forced_flush: bool = False):
    for buffer, filter, post in zip(buffers, filters, posts):
        new = process_buffer(buffer, new, filter, post, forced_flush)
        if new is None:
            return buffers

buffers = [symbol, symbols_buffer, ast]
filters = [
    dict_filter(CHAR_OPS_DICT, DEFAULT_FILTER), 
    dict_filter(SYMBOLS_DICT, DEFAULT_FILTER), 
    dict_filter(CMDS_DICT, DEFAULT_FILTER)
]

posts = [POST_SYMBOL, POST_SYMBOLS_BUFFER, lambda x: x]

for line in sys.stdin:
    for char in line:
        process_buffers(buffers, filters, posts, char)
        continue
        new = process_buffer(symbol, char, dict_filter(CHAR_OPS_DICT, DEFAULT_FILTER), POST_SYMBOL)    
        tmp = new
        if tmp is None:
            continue
        hold_symbols_buffer = SYMBOLS_DICT.get(tmp, DEFAULT_FILTER)(symbols_buffer, tmp)
        symbol = []
        if hold_symbols_buffer:
            continue
        tmp = POST_SYMBOLS_BUFFER(symbols_buffer)
        # print({tmp})
        hold_ast = CMDS_DICT.get(tmp, DEFAULT_FILTER)(ast, tmp)
        symbols_buffer = []

hold_symbol_buffer = CHAR_OPS_DICT.get(char, DEFAULT_FILTER)(symbol, char)
tmp = POST_SYMBOL(symbol)
hold_symbols_buffer = SYMBOLS_DICT.get(tmp, DEFAULT_FILTER)(symbols_buffer, tmp)
symbol = []
tmp = POST_SYMBOLS_BUFFER(symbols_buffer)
# print({tmp})
hold_ast = CMDS_DICT.get(tmp, DEFAULT_FILTER)(ast, tmp)
symbols_buffer = []
print(ast)
