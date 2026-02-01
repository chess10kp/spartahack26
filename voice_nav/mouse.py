"""Mouse functions using ydotool."""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING
import subprocess

from mouse_enums import MouseButton, MouseButtonState

if TYPE_CHECKING:
    from collections.abc import Iterable


def move(x: int, y: int, absolute: bool = True):
    """Move mouse to position.

    :param x: X position.
    :param y: Y position.
    :param absolute: Whether position is absolute.
    """
    if absolute:
        subprocess.run(["ydotool", "mousemove", "-x", str(x), "-y", str(y)])
    else:
        subprocess.run(
            ["ydotool", "mousemove", "--relative", "-x", str(x), "-y", str(y)]
        )


def click(
    x: int,
    y: int,
    button: MouseButton,
    button_states: Iterable[MouseButtonState],
    repeat: int = 1,
    absolute: bool = True,
):
    """Click at position.

    :param x: X position to click.
    :param y: Y position to click.
    :param button: Button to use.
    :param button_states: Button states (DOWN, UP).
    :param repeat: Times to repeat click.
    :param absolute: Whether position is absolute.
    """
    for _ in range(repeat):
        move(x, y, absolute=absolute)
        sleep(0.05)

        for state in button_states:
            if state == MouseButtonState.DOWN:
                if button == MouseButton.LEFT:
                    subprocess.run(["ydotool", "click", "0x1"])
                elif button == MouseButton.RIGHT:
                    subprocess.run(["ydotool", "click", "0x3"])
            elif state == MouseButtonState.UP:
                if button == MouseButton.LEFT:
                    subprocess.run(["ydotool", "click", "0x1", "--up"])
                elif button == MouseButton.RIGHT:
                    subprocess.run(["ydotool", "click", "0x3", "--up"])
            sleep(0.05)
