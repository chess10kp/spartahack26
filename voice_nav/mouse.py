"""Mouse functions using pynput."""

from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from mouse_enums import MouseButton, MouseButtonState
from pynput import mouse

if TYPE_CHECKING:
    from collections.abc import Iterable


def move(x: int, y: int, absolute: bool = True):
    """Move mouse to position.

    :param x: X position.
    :param y: Y position.
    :param absolute: Whether position is absolute.
    """
    if absolute:
        mouse.Controller().position = (x, y)
    else:
        current = mouse.Controller().position
        mouse.Controller().position = (current[0] + x, current[1] + y)


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
    controller = mouse.Controller()

    for _ in range(repeat):
        move(x, y, absolute=absolute)
        sleep(0.05)

        for state in button_states:
            if state == MouseButtonState.DOWN:
                if button == MouseButton.LEFT:
                    controller.press(mouse.Button.left)
                elif button == MouseButton.RIGHT:
                    controller.press(mouse.Button.right)
            elif state == MouseButtonState.UP:
                if button == MouseButton.LEFT:
                    controller.release(mouse.Button.left)
                elif button == MouseButton.RIGHT:
                    controller.release(mouse.Button.right)
            sleep(0.05)
