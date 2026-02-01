"""Keyboard typing helpers using ydotool."""

import subprocess


def type_text(text: str, delay: float = 0.01):
    """Paste the text via Ctrl+V using ydotool and wl-copy."""
    subprocess.run(["wl-copy"], input=text, text=True)
    subprocess.run(["ydotool", "key", "29:1", "47:1", "47:0", "29:0"])
