import PIL.ImageGrab
import datetime
import os
import logging
from pynput import keyboard

from element_selector import run_element_selection
from stt_elevenlabs import transcribe_from_mic, ElevenLabsSTTError
from typing_control import type_text


def take_screenshot():
    """Take a screenshot and save it."""
    logging.debug("Starting screenshot capture")
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("screenshots", f"screenshot_{timestamp}.png")
    screenshot = PIL.ImageGrab.grab()
    screenshot.save(filename)
    logging.debug(f"Screenshot saved as {filename}")
    return filename


def on_hotkey():
    """Hotkey handler to trigger element selection."""
    logging.info("Element selection hotkey pressed")
    try:
        run_element_selection()
    except ModuleNotFoundError as e:
        if "gi" in str(e):
            logging.warning("PyGObject/GTK not available; falling back to pygame selector")
            try:
                from element_selector_cli import run_element_selection_cli

                run_element_selection_cli()
            except Exception as inner:
                logging.error(f"Fallback selector failed: {inner}")
        else:
            logging.error(f"Element selection failed: {e}")


def on_voice_hotkey():
    """Hotkey handler to capture speech and type it if prefixed with 'type'."""
    logging.info("Voice hotkey pressed; recording...")
    try:
        transcript = transcribe_from_mic()
        logging.info(f"Heard: {transcript}")
        print(f"Heard: {transcript}")

        lower = transcript.lower().strip()
        if lower.startswith("type "):
            payload = transcript[5:]
            logging.info(f"Typing: {payload}")
            type_text(payload)
        elif lower == "type":
            logging.info("Heard bare 'type' with no content; ignoring")
        else:
            logging.info("Transcript not a type command; ignoring")
    except ElevenLabsSTTError as e:
        logging.error(f"STT error: {e}")
    except Exception as e:
        logging.error(f"Voice hotkey failed: {e}")


def start_hotkey_listener():
    """Start global hotkey listeners for element selection and voice typing."""
    logging.debug("Setting up hotkeys: E (select) and Ctrl+Alt+V (voice type)")

    pressed = set()

    def on_press(key):
        pressed.add(key)

        # Single-key trigger for selection
        if isinstance(key, keyboard.KeyCode) and key.char == "e":
            on_hotkey()

        # Chord trigger for voice typing
        ctrl = keyboard.Key.ctrl_l in pressed or keyboard.Key.ctrl_r in pressed
        alt = keyboard.Key.alt_l in pressed or keyboard.Key.alt_r in pressed
        v_key = isinstance(key, keyboard.KeyCode) and key.char == "v"
        if ctrl and alt and v_key:
            on_voice_hotkey()

    def on_release(key):
        pressed.discard(key)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    return listener
def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logging.info("Voice Navigation System starting")
    print("Voice Navigation System Started")
    print("Press E to enter element selection mode")
    print("Press Ctrl+Alt+V then say 'type <text>' to type text via ElevenLabs STT")
    print("Press Ctrl+C to exit")

    listener = start_hotkey_listener()
    logging.debug("Hotkey listener started")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down...")
        listener.stop()


if __name__ == "__main__":
    main()
