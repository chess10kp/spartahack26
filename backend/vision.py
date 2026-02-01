"""Vision module for screenshot capture and element detection."""

import logging
import uuid
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

from schemas import Block
from child import Child

logger = logging.getLogger(__name__)


def capture_screen():
    """Capture full screen screenshot.

    :return: Screenshot image.
    """
    return PIL.ImageGrab.grab()


def detect_elements(
    image,
    canny_min_val: int = 50,
    canny_max_val: int = 150,
    kernel_size: int = 3,
    min_width: int = 20,
    min_height: int = 20,
    max_width: int = 800,
    max_height: int = 600,
    max_aspect_ratio: float = 6.0,
    max_elements: int = 150,
) -> list[Child]:
    """Detect UI elements using OpenCV edge detection with simple filters.

    :param image: PIL Image to detect elements in.
    :param canny_min_val: Canny edge detection minimum threshold.
    :param canny_max_val: Canny edge detection maximum threshold.
    :param kernel_size: Size of dilation kernel.
    :param min_width: Minimum element width to consider.
    :param min_height: Minimum element height to consider.
    :param max_width: Maximum element width to consider.
    :param max_height: Maximum element height to consider.
    :param max_aspect_ratio: Maximum aspect ratio to consider.
    :param max_elements: Maximum number of elements to return.
    :return: List of Child elements detected.
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

    children.sort(
        key=lambda c: (int(c.absolute_position[1]), int(c.absolute_position[0]))
    )

    if len(children) > max_elements:
        logger.debug(f"Capping elements from {len(children)} to {max_elements}")
        children = children[:max_elements]

    logger.info(f"Detected {len(children)} elements after filtering")

    return children


def children_to_blocks(
    children: list[Child], image_width: int, image_height: int
) -> list[Block]:
    """Convert Child elements to Block format.

    :param children: List of Child elements.
    :param image_width: Width of the screenshot.
    :param image_height: Height of the screenshot.
    :return: List of Block objects.
    """
    blocks = []
    for i, child in enumerate(children):
        block = Block(
            id=str(uuid.uuid4()),
            x=child.absolute_position[0],
            y=child.absolute_position[1],
            w=child.width,
            h=child.height,
            label=f"element_{i}",
            score=1.0,
            text=None,
        )
        blocks.append(block)
    return blocks


async def enrich_blocks_with_ocr(
    screenshot_bytes: bytes, blocks: list[Block]
) -> list[Block]:
    """Enrich blocks with OCR text.

    :param screenshot_bytes: Screenshot image bytes.
    :param blocks: List of blocks to enrich.
    :return: List of enriched blocks.
    """
    return blocks


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
