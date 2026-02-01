"""Speech-to-text transcription module."""

import asyncio
import logging
import os
import subprocess
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

_whisper_model = None


def get_model(model_name: str = "base"):
    """Get or load the Whisper model.

    Args:
        model_name: Name of the Whisper model (tiny, base, small, medium, large)

    Returns:
        Loaded Whisper model
    """
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper

            logger.info(f"Loading Whisper model: {model_name}")
            _whisper_model = whisper.load_model(model_name)
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.error(
                "Whisper not installed. Install with: pip install openai-whisper"
            )
            raise
    return _whisper_model


async def transcribe_audio_file(audio_path: str) -> str:
    """Transcribe audio file to text.

    Args:
        audio_path: Path to the audio file

    Returns:
        Transcribed text
    """
    try:
        model = get_model()
        result = model.transcribe(audio_path)
        text = (result.get("text") or "").strip()
        logger.info(f"Transcribed: {text}")
        return text
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""


async def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribe audio bytes to text.

    Args:
        audio_bytes: Audio file bytes

    Returns:
        Transcribed text
    """
    import io

    with tempfile.NamedTemporaryFile(delete=False, suffix=".input") as f:
        f.write(audio_bytes)
        in_path = f.name

    try:
        out_path = in_path + ".wav"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                in_path,
                "-ac",
                "1",
                "-ar",
                "16000",
                "-vn",
                out_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        text = await transcribe_audio_file(out_path)

        for p in [in_path, out_path]:
            try:
                os.remove(p)
            except:
                pass

        return text
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        for p in [in_path, in_path + ".wav"]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except:
                pass
        return ""


def transcribe_sync(audio_path: str) -> str:
    """Synchronous wrapper for transcription.

    Args:
        audio_path: Path to the audio file

    Returns:
        Transcribed text
    """
    return asyncio.run(transcribe_audio_file(audio_path))
