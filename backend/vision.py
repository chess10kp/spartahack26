from typing import List
from schemas import Block

async def enrich_blocks_with_ocr(screenshot_bytes: bytes, blocks: List[Block]) -> List[Block]:
    # MVP: run OCR on full screen or per block crops.
    return blocks
