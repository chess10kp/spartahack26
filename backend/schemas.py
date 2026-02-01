from pydantic import BaseModel
from typing import List, Optional, Literal

class Block(BaseModel):
    id: str
    x: float  # normalized 0..1 OR pixels, but be consistent
    y: float
    w: float
    h: float
    label: Optional[str] = None
    score: Optional[float] = None
    text: Optional[str] = None  # if OCR added

class Command(BaseModel):
    action: Literal["click","double_click","right_click","type","scroll","open","noop","ask_clarification"]
    target: Optional[dict] = None
    text: Optional[str] = None
    scroll: Optional[dict] = None
    confidence: float = 0.0
    reason: Optional[str] = None

class ResolveResponse(BaseModel):
    transcript: str
    command: Command
