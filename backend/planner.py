from schemas import Command, Block
from typing import List

async def decide_command(transcript: str, screenshot_bytes: bytes, blocks: List[Block]) -> Command:
    t = transcript.lower().strip()

    # Ultra-MVP fallback rules
    if t == "click" and blocks:
        # example: click the "most confident" block if labels exist
        return Command(action="click", target={"block_id": blocks[0].id}, confidence=0.4, reason="fallback")

    # Real version: send (transcript + blocks + maybe OCR text + screenshot) to AI model
    return Command(action="ask_clarification", confidence=0.2, reason="not enough info")
