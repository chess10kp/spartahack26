"""Simple element selector using CLI instead of GTK overlay."""

import logging
from itertools import product
from math import ceil, log

import PIL.ImageGrab
from cv2 import (
    CHAIN_APPROX_SIMPLE,
    COLOR_BGR2GRAY,
    RETR_LIST,
    Canny,
    boundingRect,
    cvtColor,
    dilate,
    findContours,
)
from numpy import array, ones, uint8

from child import Child
from mouse import click
from mouse_enums import MouseButton, MouseButtonState

logger = logging.getLogger(__name__)


def capture_screen():
    """Capture full screen screenshot."""
    return PIL.ImageGrab.grab()


def detect_elements(
    image,
    canny_min_val: int = 50,
    canny_max_val: int = 150,
    kernel_size: int = 3,
):
    """Detect UI elements using OpenCV edge detection."""
    children = []

    gray_image = cvtColor(array(image), COLOR_BGR2GRAY)

    edges = Canny(gray_image, canny_min_val, canny_max_val)

    kernel = ones((kernel_size, kernel_size), uint8)
    dilated_edges = dilate(edges, kernel)

    contours, _ = findContours(dilated_edges, RETR_LIST, CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = boundingRect(contour)

        if w > 20 and h > 20 and w < 800 and h < 600:
            children.append(
                Child(
                    absolute_position=(x, y),
                    relative_position=(x, y),
                    width=w,
                    height=h,
                )
            )

    logger.info(f"Detected {len(children)} elements")
    return children


def get_hints(children, alphabet: str = "asdfghjkl"):
    """Generate hint mapping from alphabet to detected elements."""
    hints = {}

    if len(children) == 0:
        return hints

    for child, hint in zip(
        children,
        product(alphabet, repeat=ceil(log(len(children)) / log(len(alphabet)))),
    ):
        hints["".join(hint)] = child

    return hints


def run_element_selection_cli():
    """Run element selection using CLI."""
    logger.info("Starting element selection mode")

    try:
        screenshot = capture_screen()
        children = detect_elements(screenshot)
        hints = get_hints(children)

        print(f"\nDetected {len(hints)} elements:")
        print("\nType hint to select element, or 'q' to quit:")
        print("\nElements:")
        for i, (hint, child) in enumerate(list(hints.items())[:50]):
            x, y = child.absolute_position
            print(f"  {hint}: Position ({x}, {y}), Size {child.width}x{child.height}")

        if len(hints) > 50:
            print(f"  ... and {len(hints) - 50} more")

        while True:
            user_input = input("\nEnter hint: ").strip().lower()

            if user_input == "q":
                print("Quitting...")
                break

            if user_input in hints:
                child = hints[user_input]
                x, y = child.absolute_position
                center_x = int(x + child.width / 2)
                center_y = int(y + child.height / 2)

                logger.info(f"Clicking at ({center_x}, {center_y})")
                click(
                    center_x,
                    center_y,
                    MouseButton.LEFT,
                    (MouseButtonState.DOWN, MouseButtonState.UP),
                    1,
                )
                print(f"Clicked at ({center_x}, {center_y})")
                break
            else:
                print(f"Invalid hint. Try again.")

    except Exception as e:
        logger.error(f"Element selection failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    run_element_selection_cli()
