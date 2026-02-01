"""Common mouse enums."""

from enum import Enum


class MouseButton(Enum):
    """Mouse Buttons."""

    LEFT = 1
    RIGHT = 2


class MouseButtonState(Enum):
    """Mouse Button States."""

    DOWN = 1
    UP = 0


class MouseMode(Enum):
    """Mouse modes."""

    MOVE = 1
    SCROLL = 2
