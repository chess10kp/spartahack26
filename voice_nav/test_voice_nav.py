"""Test script for voice navigation system."""

import asyncio
import logging

from main import resolve_screenshot_only, run_demo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_screenshot_detection():
    """Test screenshot detection."""
    logger.info("Testing screenshot detection...")
    result = await resolve_screenshot_only()

    if result.blocks:
        logger.info(f"✓ Detected {len(result.blocks)} blocks")
        logger.info(f"✓ Command: {result.command.action}")
    else:
        logger.warning("No blocks detected")


async def test_demo():
    """Run the demo."""
    await run_demo()


async def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Voice Navigation Tests")
    print("=" * 60)

    await test_screenshot_detection()
    print("\n")
    await test_demo()

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
