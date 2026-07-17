import sys

DIVISIOR_OPS = " \n"
GROUPER_OPS = ","
IGNORED_CHARS = ""

print("Enter Ctrl + Z and Enter on WIndows or Ctrl + D on UNIX-like to send EOF")
symbol = ""
symbols_buffer = []
ast = []
for line in sys.stdin:
    for char in line:
        if char in DIVISIOR_OPS:
            if symbol == "":
                continue
            symbols_buffer.append(symbol)
            symbol = ""
            continue
        if char == GROUPER_OPS:
            ast.append(symbols_buffer)
            symbols_buffer = []
            continue
        if char in IGNORED_CHARS:
            continue
        symbol += char
        # print(f"{char = }")

ast.extend(symbols_buffer)
print(ast)
