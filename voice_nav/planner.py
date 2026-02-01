"""AI Planner for voice commands - decides actions based on intent."""

import logging
import re
from typing import Optional, List

from schemas import Block, Command

logger = logging.getLogger(__name__)


async def plan_command(
    transcript: str, blocks: List[Block], screenshot_bytes: Optional[bytes] = None
) -> Command:
    """Plan a command based on transcript and detected blocks.

    Args:
        transcript: User's spoken command
        blocks: List of detected UI elements
        screenshot_bytes: Optional screenshot for context

    Returns:
        Command object with action and target
    """
    t = transcript.lower().strip()

    if not t:
        return Command(
            action="noop", target=None, confidence=0.0, reason="No transcript provided"
        )

    logger.info(f"Planning command for transcript: '{t}'")

    click_keywords = ["click", "select", "choose", "press"]
    double_click_keywords = ["double click", "open", "launch"]
    right_click_keywords = ["right click", "context menu", "properties"]
    type_keywords = ["type", "enter", "write", "input"]
    scroll_keywords = ["scroll", "down", "up"]

    if any(keyword in t for keyword in click_keywords):
        target_block = _find_target_block(t, blocks)
        if target_block:
            return Command(
                action="click",
                target={"block_id": target_block.id, "hint": target_block.hint},
                confidence=0.8,
                reason=f"Matched '{t}' to block '{target_block.label}'",
            )
        elif blocks:
            return Command(
                action="ask_clarification",
                target=None,
                confidence=0.3,
                reason="Click requested but no matching block found",
            )

    if any(keyword in t for keyword in double_click_keywords):
        target_block = _find_target_block(t, blocks)
        if target_block:
            return Command(
                action="double_click",
                target={"block_id": target_block.id, "hint": target_block.hint},
                confidence=0.8,
                reason=f"Double-click on '{target_block.label}'",
            )

    if any(keyword in t for keyword in right_click_keywords):
        target_block = _find_target_block(t, blocks)
        if target_block:
            return Command(
                action="right_click",
                target={"block_id": target_block.id, "hint": target_block.hint},
                confidence=0.8,
                reason=f"Right-click on '{target_block.label}'",
            )

    if any(keyword in t for keyword in type_keywords):
        text_to_type = _extract_text_to_type(t)
        if text_to_type:
            return Command(
                action="type",
                target=None,
                text=text_to_type,
                confidence=0.7,
                reason=f"Type '{text_to_type}'",
            )

    if any(keyword in t for keyword in scroll_keywords):
        direction = "down" if "down" in t else "up"
        return Command(
            action="scroll",
            scroll={"direction": direction, "amount": 500},
            confidence=0.9,
            reason=f"Scroll {direction}",
        )

    return Command(
        action="ask_clarification",
        target=None,
        confidence=0.2,
        reason=f"Could not understand intent from: '{t}'",
    )


def _find_target_block(transcript: str, blocks: List[Block]) -> Optional[Block]:
    """Find the most relevant block based on transcript.

    Args:
        transcript: User's spoken command
        blocks: List of detected blocks

    Returns:
        Best matching block or None
    """
    if not blocks:
        return None

    words = transcript.lower().split()

    scored_blocks = []
    for block in blocks:
        score = 0.0

        if block.text:
            for word in words:
                if word in block.text.lower():
                    score += 1.0

        if block.label:
            for word in words:
                if word in block.label.lower():
                    score += 0.5

        if block.hint:
            for word in words:
                if word == block.hint.lower():
                    score += 2.0

        if score > 0:
            scored_blocks.append((score, block))

    if scored_blocks:
        scored_blocks.sort(key=lambda x: x[0], reverse=True)
        return scored_blocks[0][1]

    return blocks[0]


def _extract_text_to_type(transcript: str) -> Optional[str]:
    """Extract text to type from transcript.

    Args:
        transcript: User's spoken command

    Returns:
        Text to type or None
    """
    patterns = [
        r"type\s+(.*)",
        r"enter\s+(.*)",
        r"write\s+(.*)",
        r"input\s+(.*)",
    ]

    for pattern in patterns:
        match = re.search(pattern, transcript.lower())
        if match:
            text = match.group(1).strip("'\"")
            if text:
                return text

    return None


def _find_number(transcript: str) -> Optional[int]:
    """Extract a number from transcript.

    Args:
        transcript: User's spoken command

    Returns:
        Number or None
    """
    numbers = re.findall(r"\d+", transcript)
    if numbers:
        return int(numbers[0])
    return None
