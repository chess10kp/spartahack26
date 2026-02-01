import PIL.ImageGrab
import datetime
import os
import logging
from pynput import keyboard

from element_selector_cli import run_element_selection_cli


def take_screenshot():
    """Take a screenshot and save it."""
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("screenshots", f"screenshot_{timestamp}.png")
    screenshot = PIL.ImageGrab.grab()
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")
    return filename


def on_hotkey():
    """Hotkey handler to trigger element selection."""
    logging.info("Element selection hotkey pressed")
    run_element_selection_cli()


def start_hotkey_listener():
    """Start global hotkey listener for element selection."""
    hotkey = keyboard.HotKey(keyboard.HotKey.parse("<ctrl>+<alt>+e"), on_hotkey)

    def on_press(k):
        if k is not None:
            hotkey.press(k)

    def on_release(k):
        if k is not None:
            hotkey.release(k)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    print("Voice Navigation System Started")
    print("Press Ctrl+Alt+E to enter element selection mode")
    print("Press Ctrl+C to exit")

    listener = start_hotkey_listener()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down...")
        listener.stop()


if __name__ == "__main__":
    main()
