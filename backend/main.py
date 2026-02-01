"""Main FastAPI backend with complete flow integration."""

import io
import logging

import PIL.Image
from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional, Dict, Any

from schemas import ResolveResponse, Block, Command
from stt import transcribe_audio
from vision import (
    capture_screen,
    detect_elements,
    children_to_blocks,
    enrich_blocks_with_ocr,
)
from planner import decide_command

logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Multimodal Hands-Free Interface Backend API"}


@app.post("/command/resolve", response_model=ResolveResponse)
async def resolve_command(
    audio: UploadFile = File(None),
    screenshot: UploadFile = File(None),
    blocks_json: Optional[str] = Form(None),
    screenshot_only: Optional[bool] = Form(False),
):
    """Resolve voice command with optional screenshot and detected blocks.

    Args:
        audio: Optional audio file for speech-to-text.
        screenshot: Optional screenshot image.
        blocks_json: Optional JSON string of pre-detected blocks.
        screenshot_only: If True, return detected blocks without voice processing.

    Returns:
        ResolveResponse with transcript and command.
    """
    transcript = ""
    blocks = []
    screenshot_bytes = None

    if screenshot:
        screenshot_bytes = await screenshot.read()
        image = PIL.Image.open(io.BytesIO(screenshot_bytes))
        logger.info(f"Received screenshot of size {image.size}")
    else:
        logger.info("No screenshot provided, capturing screen...")
        image = capture_screen()
        screenshot_bytes = io.BytesIO()
        image.save(screenshot_bytes, format="PNG")
        screenshot_bytes.seek(0)
        screenshot_bytes = screenshot_bytes.getvalue()

    if not blocks_json:
        logger.info("Detecting elements from screenshot...")
        children = detect_elements(image)
        blocks = children_to_blocks(children, image.width, image.height)
    else:
        import json

        raw = json.loads(blocks_json)
        blocks = [
            Block(**b)
            for b in raw.get("blocks", [raw] if isinstance(raw, dict) else raw)
        ]
        logger.info(f"Using {len(blocks)} provided blocks")

    if screenshot_only:
        command = Command(
            action="noop",
            target={"blocks": [b.model_dump() for b in blocks]},
            confidence=1.0,
            reason="Screenshot only mode",
        )
        return ResolveResponse(transcript=transcript, command=command)

    if audio:
        logger.info("Transcribing audio...")
        transcript = await transcribe_audio(audio)
        logger.info(f"Transcript: {transcript}")
    else:
        logger.warning("No audio provided")

    blocks = await enrich_blocks_with_ocr(screenshot_bytes, blocks)

    if transcript:
        command = await decide_command(
            transcript=transcript, screenshot_bytes=screenshot_bytes, blocks=blocks
        )
    else:
        command = Command(
            action="noop", target=None, confidence=0.0, reason="No transcript provided"
        )

    return ResolveResponse(transcript=transcript, command=command)


@app.post("/screenshot/detect")
async def screenshot_detect(
    screenshot: UploadFile = File(None),
):
    """Detect elements from screenshot and return blocks.

    Args:
        screenshot: Optional screenshot image. If not provided, captures screen.

    Returns:
        JSON with detected blocks and screenshot info.
    """
    if screenshot:
        screenshot_bytes = await screenshot.read()
        image = PIL.Image.open(io.BytesIO(screenshot_bytes))
    else:
        image = capture_screen()
        screenshot_bytes = io.BytesIO()
        image.save(screenshot_bytes, format="PNG")
        screenshot_bytes.seek(0)
        screenshot_bytes = screenshot_bytes.getvalue()

    children = detect_elements(image)
    blocks = children_to_blocks(children, image.width, image.height)

    return {
        "image_width": image.width,
        "image_height": image.height,
        "num_blocks": len(blocks),
        "blocks": [b.model_dump() for b in blocks],
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)
