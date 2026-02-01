"""Test script for complete backend flow (without STT dependency)."""

import asyncio
import logging
import sys
import os
import io

sys.path.insert(0, os.path.dirname(__file__))

from schemas import Command, Block
from vision import capture_screen, detect_elements, children_to_blocks
from planner import decide_command

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_complete_flow():
    """Test the complete flow: screenshot -> detect -> transcribe -> plan."""
    logger.info("=" * 60)
    logger.info("Starting Complete Backend Flow Test")
    logger.info("=" * 60)

    image = capture_screen()
    logger.info(f"[Step 1] Captured screenshot of size {image.size}")

    children = detect_elements(image)
    logger.info(f"[Step 2] Detected {len(children)} elements")

    blocks = children_to_blocks(children, image.width, image.height)
    logger.info(f"[Step 3] Created {len(blocks)} blocks")

    screenshot_bytes = io.BytesIO()
    image.save(screenshot_bytes, format="PNG")
    screenshot_bytes.seek(0)
    screenshot_bytes = screenshot_bytes.getvalue()
    logger.info(
        f"[Step 4] Converted screenshot to bytes ({len(screenshot_bytes)} bytes)"
    )

    test_transcript = "click the first button"
    logger.info(f"[Step 5] Using test transcript: '{test_transcript}'")

    command = await decide_command(
        transcript=test_transcript, screenshot_bytes=screenshot_bytes, blocks=blocks
    )
    logger.info(f"[Step 6] AI Planner returned command:")
    logger.info(f"         Action: {command.action}")
    logger.info(f"         Target: {command.target}")
    logger.info(f"         Confidence: {command.confidence}")
    logger.info(f"         Reason: {command.reason}")

    logger.info("=" * 60)
    logger.info("Complete Flow Test Finished Successfully!")
    logger.info("=" * 60)


async def test_screenshot_detection_only():
    """Test just the screenshot detection part."""
    logger.info("Testing screenshot detection only...")

    image = capture_screen()
    children = detect_elements(image)
    blocks = children_to_blocks(children, image.width, image.height)

    logger.info(f"Detected {len(blocks)} blocks from screenshot")

    if blocks:
        sample = blocks[0].model_dump()
        logger.info(f"Sample block: {sample}")


async def run_all_tests():
    """Run all backend tests."""
    await test_screenshot_detection_only()
    print("\n")
    await test_complete_flow()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
