import sys
from typing import Callable

DIVISIOR_OPS = " \n"
GROUPER_OPS = ","
IGNORED_CHARS = ""


CHAR_OPS_DICT = {
    " ": lambda buffer, new: False,
    "\n": lambda buffer, new: False,
}

SYMBOLS_DICT = {"": lambda buffer, new: True, ",": lambda buffer, new: False}

DEFAULT_FILTER: Callable[[list, str], bool] = lambda buffer, new: not buffer.append(new)

print("Enter Ctrl + Z and Enter on WIndows or Ctrl + D on UNIX-like to send EOF")
symbol = []
symbols_buffer = []
ast = []
for line in sys.stdin:
    for char in line:
        hold_symbol_buffer = CHAR_OPS_DICT.get(char, DEFAULT_FILTER)(symbol, char)
        if hold_symbol_buffer:
            continue
        symbol_str = "".join(symbol)
        hold_symbols_buffer = SYMBOLS_DICT.get(symbol_str, DEFAULT_FILTER)(symbols_buffer, symbol_str)
        symbol = []
        if hold_symbols_buffer:
            continue
        ast.append(symbols_buffer)
        symbols_buffer = []
        # print(f"{char = }")

symbols_buffer.append("".join(symbol))
ast.append(symbols_buffer)
print(ast)
