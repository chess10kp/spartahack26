"""Keyboard typing helpers using ydotool."""

import subprocess
import time


def type_text(text: str, delay: float = 0.01):
    """Paste the text via Ctrl+V using ydotool and wl-copy."""
    subprocess.run(["wl-copy"], input=text, text=True, check=True)
    time.sleep(0.05)
    subprocess.run(["ydotool", "key", "29:1", "47:1", "47:0", "29:0"], check=True)
