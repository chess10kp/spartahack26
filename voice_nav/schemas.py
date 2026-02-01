"""Data models for voice navigation system."""

from pydantic import BaseModel
from typing import List, Optional, Literal


class Block(BaseModel):
    """Represents a detected UI element block."""

    id: str
    x: float  # X position in pixels
    y: float  # Y position in pixels
    w: float  # Width in pixels
    h: float  # Height in pixels
    label: Optional[str] = None
    score: Optional[float] = None
    text: Optional[str] = None  # OCR text (future)
    hint: Optional[str] = None  # Hint string for keyboard selection


class Command(BaseModel):
    """Represents a command to execute."""

    action: Literal[
        "click",
        "double_click",
        "right_click",
        "type",
        "scroll",
        "open",
        "noop",
        "ask_clarification",
    ]
    target: Optional[dict] = None
    text: Optional[str] = None
    scroll: Optional[dict] = None
    confidence: float = 0.0
    reason: Optional[str] = None


class ResolveResult(BaseModel):
    """Result of resolving a voice command."""

    transcript: str
    command: Command
    blocks: Optional[List[Block]] = None
