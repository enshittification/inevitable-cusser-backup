"""A curses wrapper that understands ANSI escape code sequences."""


from __future__ import annotations

import curses
from dataclasses import dataclass
from typing import Text

import ochre
from stransi import Ansi, SetAttribute, SetColor
from stransi.attribute import Attribute
from stransi.color import ColorRole

from .color_manager import ColorManager, ColorPair

__version__ = "0.1.0"


__all__ = ["Cusser"]


def on_add_color(color: ochre.Color, manager: ColorManager) -> None:
    """Initialize a color when it is added to the color manager."""
    color = color.rgb
    curses.init_color(
        manager[color],
        int(1000 * color.red),
        int(1000 * color.green),
        int(1000 * color.blue),
    )


def on_add_pair(pair: ColorPair, manager: ColorManager) -> None:
    """Initialize a color pair when it is added to the color manager."""
    curses.init_pair(manager[pair], manager[pair.foreground], manager[pair.background])


@dataclass
class Cusser:
    """A curses wrapper that understands ANSI escape code sequences."""

    window: curses._CursesWindow
    color_manager = ColorManager(on_add_color=on_add_color, on_add_pair=on_add_pair)

    _ON_ATTR_MAP = {
        Attribute.NORMAL: curses.A_NORMAL,
        Attribute.BOLD: curses.A_BOLD,
        Attribute.DIM: curses.A_DIM,
        Attribute.ITALIC: curses.A_ITALIC,
        Attribute.UNDERLINE: curses.A_UNDERLINE,
        Attribute.BLINK: curses.A_BLINK,
        Attribute.REVERSE: curses.A_REVERSE,
        Attribute.HIDDEN: curses.A_INVIS,
    }

    _OFF_ATTR_MAP = {
        Attribute.NEITHER_BOLD_NOR_DIM: curses.A_BOLD | curses.A_DIM,
        Attribute.NOT_ITALIC: curses.A_ITALIC,
        Attribute.NOT_UNDERLINE: curses.A_UNDERLINE,
        Attribute.NOT_BLINK: curses.A_BLINK,
        Attribute.NOT_REVERSE: curses.A_REVERSE,
        Attribute.NOT_HIDDEN: curses.A_INVIS,
    }

    def __post_init__(self):
        """Initialize the color manager."""
        curses.use_default_colors()

    def __getattr__(self, name):
        """Forward all other calls to the underlying window."""
        return getattr(self.window, name)

    def addstr(self, text: Text) -> None:
        """Add a string to the window, interpreting ANSI escape codes."""
        for instruction in Ansi(text).instructions():
            if isinstance(instruction, Text):
                self.window.addstr(instruction)
            elif isinstance(instruction, SetAttribute):
                if instruction.attribute in self._ON_ATTR_MAP:
                    self.window.attron(self._ON_ATTR_MAP[instruction.attribute])
                elif instruction.attribute in self._OFF_ATTR_MAP:
                    self.window.attroff(self._OFF_ATTR_MAP[instruction.attribute])
                else:
                    raise ValueError(f"Unknown attribute {instruction.attribute}")
            elif isinstance(instruction, SetColor):
                if instruction.role == ColorRole.FOREGROUND:
                    self.color_manager.foreground = instruction.color
                elif instruction.role == ColorRole.BACKGROUND:
                    self.color_manager.background = instruction.color
                else:
                    raise ValueError(f"Unknown color role {instruction.role}")
                self.window.attron(
                    curses.color_pair(
                        self.color_manager[self.color_manager.current_pair]
                    )
                )
            else:
                raise NotImplementedError(instruction)
