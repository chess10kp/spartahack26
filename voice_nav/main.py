import PIL.ImageGrab
import datetime
import os
import logging

from element_selector import run_element_selection


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


def trigger_element_selection():
    """Trigger element selection overlay."""
    logging.info("Element selection triggered")
    run_element_selection()


def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logging.info("Voice Navigation System starting")
    print("Voice Navigation System Started")


if __name__ == "__main__":
    main()
