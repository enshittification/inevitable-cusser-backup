"""Run a simple test of the Cusser class."""


import curses
import sys
from functools import reduce

from ._misc import (
    _SUPPORTED_ATTRIBUTE_TAGS,
    _SUPPORTED_COLOR_TAGS,
    _app,
    _clear_line,
    _clear_screen,
    _move,
    _step,
)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            f"usage: {sys.argv[0]} <example>, where <example> is one of: "
            "'attributes', 'colors', 'clear', 'cursor'"
        )
        sys.exit(1)

    message = "The quick brown fox jumps over the lazy dog"

    if sys.argv[1] == "attributes":
        text = reduce(
            lambda acc, attribute: acc + attribute(message) + "\n",
            _SUPPORTED_ATTRIBUTE_TAGS,
            "",
        )
    elif sys.argv[1] == "colors":
        text = reduce(
            lambda acc, color: acc + color(message) + "\n", _SUPPORTED_COLOR_TAGS, ""
        )
    elif sys.argv[1] == "clear":
        text = f"{message}{_clear_screen}Screen cleared!\n{message}{_clear_line}"
    elif sys.argv[1] == "cursor":
        text = f"{message}{_move()}{_step(1, 1)}{message}{_move(3, 3)}{message}"
    else:
        raise ValueError(
            f"unknown example: {sys.argv[1]}, must be one of: "
            "'attributes', 'colors', 'clear', 'cursor'"
        )

    curses.wrapper(lambda stdscr: _app(stdscr, text))
