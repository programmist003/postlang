import sys
from typing import Any, Callable, Dict, Generic, Protocol, TypeVar

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")

def _cover_list(x: list):
    covered = tuple(x)
    x.clear()
    x.append(covered)
    return True


class Filter(Protocol, Generic[T]):
    def __call__(self, buffer: list, new: T) -> bool:
        pass


class Converter(Protocol, Generic[T1, T2]):
    def __call__(self, x: T1) -> T2:
        pass


CHAR_OPS_DICT = {
    " ": lambda buffer, new: False,
    "\n": lambda buffer, new: False,
}

SYMBOLS_DICT = {"": lambda buffer, new: True, ",": lambda buffer, new: False}

CMDS_DICT: Dict[Any, Filter] = {
    tuple(): lambda ast, new: not _cover_list(ast)
}

DEFAULT_FILTER: Callable[[list, T], bool] = lambda buffer, new: not buffer.append(new)

print("Enter Ctrl + Z and Enter on WIndows or Ctrl + D on UNIX-like to send EOF")
symbol: list = []
POST_SYMBOL: Converter = lambda symbol: "".join(symbol)
symbols_buffer: list = []
POST_SYMBOLS_BUFFER: Converter = lambda x: tuple(x)
ast: list = []
for line in sys.stdin:
    for char in line:
        hold_symbol_buffer = CHAR_OPS_DICT.get(char, DEFAULT_FILTER)(symbol, char)
        if hold_symbol_buffer:
            continue
        tmp = POST_SYMBOL(symbol)
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
