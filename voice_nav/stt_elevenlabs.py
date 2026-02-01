import os
import tempfile
from typing import Optional

import requests
import sounddevice as sd
import soundfile as sf

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_RATE = 16000
DEFAULT_DURATION_SEC = 4
DEFAULT_MODEL_ID = "scribe_v2"


class ElevenLabsSTTError(Exception):
    pass


def record_microphone(
    duration_sec: float = DEFAULT_DURATION_SEC, sample_rate: int = DEFAULT_SAMPLE_RATE
) -> str:
    """Record audio from the default microphone and return a temp wav file path."""
    logger.info(f"Recording for {duration_sec} seconds at {sample_rate}Hz...")
    try:
        audio = sd.rec(
            int(duration_sec * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        fd, path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        sf.write(path, audio, sample_rate)
        logger.info(f"Recording saved to {path}")
        return path
    except Exception as e:
        logger.error(f"Recording failed: {e}")
        raise


def transcribe_file(
    path: str, api_key: Optional[str] = None, model_id: str = DEFAULT_MODEL_ID
) -> str:
    """Send an audio file to ElevenLabs STT and return the transcript text."""
    key = api_key or os.getenv("ELEVENLABS_API_KEY")
    if not key:
        raise ElevenLabsSTTError("Missing ELEVENLABS_API_KEY")

    logger.info(f"Sending {path} to ElevenLabs STT (model: {model_id})...")
    url = "https://api.elevenlabs.io/v1/speech-to-text"
    headers = {
        "Accept": "application/json",
        "xi-api-key": key,
    }
    with open(path, "rb") as f:
        files = {"file": (os.path.basename(path), f, "audio/wav")}
        data = {"model_id": model_id}
        resp = requests.post(url, headers=headers, files=files, data=data, timeout=30)
    logger.info(f"ElevenLabs response status: {resp.status_code}")
    if resp.status_code != 200:
        logger.error(f"ElevenLabs error response: {resp.text}")
        raise ElevenLabsSTTError(f"STT failed {resp.status_code}: {resp.text}")
    out = resp.json()
    transcript = (out.get("text") or "").strip()
    logger.info(f"Transcription result: {repr(transcript)}")
    return transcript


def transcribe_from_mic(
    duration_sec: float = DEFAULT_DURATION_SEC,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    api_key: Optional[str] = None,
) -> str:
    """Convenience: record from mic then transcribe."""
    path = record_microphone(duration_sec=duration_sec, sample_rate=sample_rate)
    try:
        return transcribe_file(path, api_key=api_key)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
