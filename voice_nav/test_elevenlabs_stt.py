"""Test script for ElevenLabs STT integration."""

import asyncio
import logging
import os

from stt_elevenlabs import (
    transcribe_from_mic,
    transcribe_file,
    record_microphone,
    ElevenLabsSTTError,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_microphone_recording():
    """Test microphone recording."""
    logger.info("Testing microphone recording...")

    try:
        temp_file = record_microphone(duration_sec=3)
        logger.info(f"✓ Audio recorded to: {temp_file}")

        file_size = os.path.getsize(temp_file)
        logger.info(f"  File size: {file_size} bytes")

        os.remove(temp_file)
        logger.info("✓ Test recording file cleaned up")
        return True
    except Exception as e:
        logger.error(f"✗ Microphone recording failed: {e}")
        return False


async def test_transcribe_file():
    """Test file transcription."""
    logger.info("\nTesting file transcription...")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.warning("⚠ ELEVENLABS_API_KEY not set, skipping file transcription test")
        return None

    try:
        temp_file = record_microphone(duration_sec=3)
        logger.info(f"  Recorded audio for transcription test")

        transcript = transcribe_file(temp_file, api_key=api_key)
        logger.info(f"✓ Transcription successful: '{transcript}'")

        os.remove(temp_file)
        logger.info("✓ Test file cleaned up")
        return transcript
    except ElevenLabsSTTError as e:
        logger.error(f"✗ ElevenLabs STT error: {e}")
        return None
    except Exception as e:
        logger.error(f"✗ File transcription failed: {e}")
        return None


async def test_transcribe_from_mic():
    """Test microphone transcription."""
    logger.info("\nTesting microphone transcription...")

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.warning(
            "⚠ ELEVENLABS_API_KEY not set, skipping microphone transcription test"
        )
        return None

    try:
        logger.info("  Please speak clearly for 4 seconds...")
        transcript = transcribe_from_mic(duration_sec=4, api_key=api_key)
        logger.info(f"✓ Transcription successful: '{transcript}'")
        return transcript
    except ElevenLabsSTTError as e:
        logger.error(f"✗ ElevenLabs STT error: {e}")
        return None
    except Exception as e:
        logger.error(f"✗ Microphone transcription failed: {e}")
        return None


async def run_all_tests():
    """Run all ElevenLabs STT tests."""
    print("=" * 60)
    print("  ElevenLabs STT Integration Tests")
    print("=" * 60)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        logger.warning("\n⚠ WARNING: ELEVENLABS_API_KEY environment variable not set")
        logger.warning("  API transcription tests will be skipped")
        logger.warning("  Set it with: export ELEVENLABS_API_KEY=your_api_key")
    else:
        logger.info("\n✓ ELEVENLABS_API_KEY is set")

    results = []

    results.append(await test_microphone_recording())
    results.append(await test_transcribe_file())
    results.append(await test_transcribe_from_mic())

    print("\n" + "=" * 60)
    print("  Test Results Summary")
    print("=" * 60)

    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    skipped = sum(1 for r in results if r is None)

    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Skipped: {skipped}")
    print(f"  Total:  {len(results)}")

    if passed == len(results):
        print("\n✓ All tests passed!")
    elif failed > 0:
        print(f"\n✗ {failed} test(s) failed")
    else:
        print("\n⚠ Some tests were skipped")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
