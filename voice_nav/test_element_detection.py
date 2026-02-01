"""Test script for element detection without GUI."""

import logging
from itertools import product
from math import ceil, log

try:
    import pyscreenshot as ImageGrab
except ImportError:
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

logging.basicConfig(level=logging.DEBUG)


class Child:
    def __init__(
        self,
        absolute_position: tuple[float, float],
        relative_position: tuple[float, float],
        width: float,
        height: float,
    ):
        self.absolute_position = absolute_position
        self.relative_position = relative_position
        self.width = width
        self.height = height


def capture_screen():
    """Capture full screen screenshot."""
    try:
        return ImageGrab.grab(backend="grim")
    except Exception:
        return PIL.ImageGrab.grab()


def detect_elements(
    image,
    canny_min_val: int = 50,
    canny_max_val: int = 150,
    kernel_size: int = 3,
    min_width: int = 20,
    min_height: int = 20,
    max_width: int = 900,
    max_height: int = 900,
    max_aspect_ratio: float = 6.0,
    max_elements: int = 150,
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

        if w < min_width or h < min_height or w > max_width or h > max_height:
            continue

        aspect = max(w, h) / max(1, min(w, h))
        if aspect > max_aspect_ratio:
            continue

        children.append(
            Child(
                absolute_position=(x, y),
                relative_position=(x, y),
                width=w,
                height=h,
            )
        )

    children.sort(
        key=lambda c: (int(c.absolute_position[1]), int(c.absolute_position[0]))
    )

    if len(children) > max_elements:
        logging.debug(f"Capping elements from {len(children)} to {max_elements}")
        children = children[:max_elements]

    logging.info(f"Detected {len(children)} elements after filtering")

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


def main():
    """Test element detection."""
    print("Capturing screen...")
    screenshot = capture_screen()
    print(f"Screenshot size: {screenshot.size}")

    print("Detecting elements...")
    children = detect_elements(screenshot)
    print(f"Found {len(children)} elements")

    print("Generating hints...")
    hints = get_hints(children)
    print(f"Generated {len(hints)} hints")

    print("\nFirst 10 hints:")
    for i, (hint, child) in enumerate(list(hints.items())[:10]):
        print(
            f"  {hint}: Position {child.absolute_position}, Size {child.width}x{child.height}"
        )


if __name__ == "__main__":
    main()
