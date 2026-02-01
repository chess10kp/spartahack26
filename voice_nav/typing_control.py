"""Keyboard typing helpers using pynput."""

from time import sleep
from pynput import keyboard


def type_text(text: str, delay: float = 0.01):
    """Type the provided text via virtual keyboard."""
    controller = keyboard.Controller()
    for ch in text:
        controller.press(ch)
        controller.release(ch)
        sleep(delay)
