"""Element selector using CV pipeline to detect clickable elements."""

from __future__ import annotations

import logging
from itertools import product
from math import ceil, log
from typing import TYPE_CHECKING

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

from child import Child
from mouse import click
from mouse_enums import MouseButton, MouseButtonState

if TYPE_CHECKING:
    from PIL.Image import Image

logger = logging.getLogger(__name__)


def capture_screen() -> Image:
    """Capture full screen screenshot.

    :return: Screenshot image.
    """
    try:
        return ImageGrab.grab(backend="grim")
    except Exception:
        return PIL.ImageGrab.grab()


def detect_elements(
    image: Image,
    canny_min_val: int = 50,
    canny_max_val: int = 150,
    kernel_size: int = 3,
    min_width: int = 20,
    min_height: int = 20,
    max_width: int = 900,
    max_height: int = 900,
    max_aspect_ratio: float = 6.0,
    max_elements: int = 150,
) -> list[Child]:
    """Detect UI elements using OpenCV edge detection with simple filters.

    Filters trim obvious noise to keep hint lists reasonable; tweak thresholds per UI.
    """
    children: list[Child] = []

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

    # Stable ordering keeps hint assignment deterministic.
    children.sort(
        key=lambda c: (int(c.absolute_position[1]), int(c.absolute_position[0]))
    )

    if len(children) > max_elements:
        logger.debug(f"Capping elements from {len(children)} to {max_elements}")
        children = children[:max_elements]

    logger.debug(f"Detected {len(children)} elements after filtering")

    return children


def get_hints(children: list[Child], alphabet: str = "asdfghjkl") -> dict[str, Child]:
    """Generate hint mapping from alphabet to detected elements.

    :param children: List of detected Child elements.
    :param alphabet: Characters to use for hints.
    :return: Dictionary mapping hint strings to Child objects.
    """
    hints: dict[str, Child] = {}

    if len(children) == 0:
        return hints

    for child, hint in zip(
        children,
        product(alphabet, repeat=ceil(log(len(children)) / log(len(alphabet)))),
    ):
        hints["".join(hint)] = child

    return hints


def on_element_selected(click_x: float, click_y: float):
    """Handle element selection by clicking.

    :param click_x: X coordinate to click.
    :param click_y: Y coordinate to click.
    """
    logger.info(f"Clicking at ({click_x}, {click_y})")
    click(
        int(click_x),
        int(click_y),
        MouseButton.LEFT,
        (MouseButtonState.DOWN, MouseButtonState.UP),
        1,
    )


def run_element_selection():
    """Run element selection flow."""
    logger.info("Starting element selection mode")

    try:
        screenshot = capture_screen()
        children = detect_elements(screenshot)
        if not children:
            logger.warning("No elements detected; aborting selection")
            return
        hints = get_hints(children)

        from gi import require_version

        require_version("Gtk", "3.0")
        require_version("Gdk", "3.0")
        from gi.repository import Gdk, Gtk

        from minimal_overlay import MinimalOverlayWindow

        config = {
            "exit_key": "Escape",
            "hints": {
                "hint_height": 30,
                "hint_width_padding": 10,
                "hint_font_size": 14,
                "hint_font_face": "Sans",
                "hint_font_r": 1.0,
                "hint_font_g": 1.0,
                "hint_font_b": 1.0,
                "hint_font_a": 1.0,
                "hint_background_r": 0.2,
                "hint_background_g": 0.2,
                "hint_background_b": 0.8,
                "hint_background_a": 0.9,
                "hint_upercase": True,
            },
        }

        overlay = MinimalOverlayWindow(
            config=config,
            hints=hints,
            on_select=on_element_selected,
        )

        overlay.show_all()
        Gtk.main()

        logger.info("Element selection completed")

    except Exception as e:
        logger.error(f"Element selection failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    run_element_selection()
