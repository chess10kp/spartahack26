from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
import json

from schemas import ResolveResponse, Block
from stt import transcribe_audio
from vision import enrich_blocks_with_ocr  # optional
from planner import decide_command

app = FastAPI()

@app.post("/command/resolve", response_model=ResolveResponse)
async def resolve_command(
    audio: UploadFile = File(...),
    screenshot: UploadFile = File(...),
    blocks_json: Optional[str] = Form(None),  # blocks metadata from CV
):
    # 1) STT
    transcript = await transcribe_audio(audio)

    # 2) Parse blocks
    blocks = []
    if blocks_json:
      raw = json.loads(blocks_json)
      blocks = [Block(**b) for b in raw.get("blocks", raw)]

    # 3) Optionally OCR blocks (or do OCR earlier in CV pipeline)
    # screenshot bytes available if needed
    shot_bytes = await screenshot.read()
    blocks = await enrich_blocks_with_ocr(shot_bytes, blocks)  # can be no-op

    # 4) Decide action using AI (LLM/VLM)
    command = await decide_command(
        transcript=transcript,
        screenshot_bytes=shot_bytes,
        blocks=blocks
    )

    return ResolveResponse(transcript=transcript, command=command)
