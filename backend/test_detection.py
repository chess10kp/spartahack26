"""Test script for backend detection integration."""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from vision import capture_screen, detect_elements, children_to_blocks, get_hints
from schemas import Block

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_detection():
    """Test the detection pipeline."""
    logger.info("Starting detection test...")

    image = capture_screen()
    logger.info(f"Captured screenshot of size {image.size}")

    children = detect_elements(image)
    logger.info(f"Detected {len(children)} elements")

    blocks = children_to_blocks(children, image.width, image.height)
    logger.info(f"Created {len(blocks)} blocks")

    hints = get_hints(children)
    logger.info(f"Generated {len(hints)} hints")

    if len(blocks) > 0:
        logger.info(f"Sample block: {blocks[0].dict()}")
    if len(hints) > 0:
        first_hint = list(hints.keys())[0]
        logger.info(f"Sample hint '{first_hint}' -> {hints[first_hint].__dict__}")

    logger.info("Detection test completed!")


if __name__ == "__main__":
    asyncio.run(test_detection())
