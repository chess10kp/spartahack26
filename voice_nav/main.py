"""Main voice navigation system with complete flow integration."""

import asyncio
import io
import logging
import os
import subprocess
import sys
import time

from PIL import Image

try:
    import pyscreenshot as ImageGrab
except ImportError:
    from PIL import ImageGrab

from schemas import Block, Command, ResolveResult
from stt import transcribe_audio_file
from stt_elevenlabs import transcribe_from_mic, ElevenLabsSTTError
from planner import plan_command
from element_selector import detect_elements, get_hints, run_element_selection
from child import Child
from mouse import click, move
from mouse_enums import MouseButton, MouseButtonState
from typing_control import type_text
import evdev
import select
from ai_client import query_openrouter_with_vision, OpenRouterError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def take_screenshot():
    """Take a screenshot and save it."""
    os.makedirs("screenshots", exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("screenshots", f"screenshot_{timestamp}.png")
    try:
        screenshot = ImageGrab.grab(backend="grim")
    except Exception:
        screenshot = ImageGrab.grab()
    screenshot.save(filename)
    logger.info(f"Screenshot saved as {filename}")
    return filename, screenshot


def on_hotkey():
    """Hotkey handler to trigger element selection."""
    logging.info("Element selection hotkey pressed")
    from element_selector_cli import run_element_selection_cli

    run_element_selection_cli()


def trigger_element_selection():
    """Trigger element selection (called from external modules)."""
    import os
    import sys

    voice_nav_dir = os.path.dirname(__file__)
    if voice_nav_dir not in sys.path:
        sys.path.insert(0, voice_nav_dir)
    from element_selector_cli import run_element_selection_cli

    run_element_selection_cli()


def children_to_blocks(children: list[Child], hints: dict[str, Child]) -> list[Block]:
    """Convert Child elements to Block format.

    Args:
        children: List of Child elements
        hints: Hint mapping

    Returns:
        List of Block objects
    """
    import uuid

    blocks = []
    for i, child in enumerate(children):
        hint_key = next((k for k, v in hints.items() if v == child), None)
        block = Block(
            id=str(uuid.uuid4()),
            x=child.absolute_position[0],
            y=child.absolute_position[1],
            w=child.width,
            h=child.height,
            label=f"element_{i}",
            score=1.0,
            text=None,
            hint=hint_key,
        )
        blocks.append(block)
    return blocks


async def execute_command(command: Command):
    """Execute a command.

    Args:
        command: Command to execute
    """
    logger.info(f"Executing command: {command.action}")

    if command.action == "click":
        if command.target and "block_id" in command.target:
            block_id = command.target["block_id"]
            block = _find_block_by_id(block_id)
            if block:
                center_x = int(block.x + block.w / 2)
                center_y = int(block.y + block.h / 2)
                logger.info(f"Clicking at ({center_x}, {center_y})")
                click(
                    center_x,
                    center_y,
                    MouseButton.LEFT,
                    (MouseButtonState.DOWN, MouseButtonState.UP),
                    1,
                )

    elif command.action == "double_click":
        if command.target and "block_id" in command.target:
            block_id = command.target["block_id"]
            block = _find_block_by_id(block_id)
            if block:
                center_x = int(block.x + block.w / 2)
                center_y = int(block.y + block.h / 2)
                logger.info(f"Double-clicking at ({center_x}, {center_y})")
                click(
                    center_x,
                    center_y,
                    MouseButton.LEFT,
                    (MouseButtonState.DOWN, MouseButtonState.UP),
                    2,
                )

    elif command.action == "type":
        if command.text:
            type_text(command.text)
            logger.info(f"Typed: {command.text}")

    elif command.action == "scroll":
        if command.scroll:
            direction = command.scroll.get("direction", "down")
            amount = command.scroll.get("amount", 500)
            scroll_amount = amount // 100
            if direction == "down":
                for _ in range(scroll_amount):
                    subprocess.run(["ydotool", "key", "108:1", "108:0"])
            else:
                for _ in range(scroll_amount):
                    subprocess.run(["ydotool", "key", "109:1", "109:0"])
            logger.info(f"Scrolled {direction} by {amount}")

    elif command.action == "noop":
        logger.info("No action taken")

    elif command.action == "ask_clarification":
        logger.warning(f"Clarification needed: {command.reason}")


_current_blocks: list[Block] = []


def _find_block_by_id(block_id: str) -> Block:
    """Find a block by ID.

    Args:
        block_id: Block ID to find

    Returns:
        Block object
    """
    for block in _current_blocks:
        if block.id == block_id:
            return block
    raise ValueError(f"Block not found: {block_id}")


async def resolve_voice_command(audio_path: str) -> ResolveResult:
    """Complete flow: screenshot → detect → transcribe → plan.

    Args:
        audio_path: Path to audio file with voice command

    Returns:
        ResolveResult with transcript and command
    """
    global _current_blocks

    logger.info("=" * 60)
    logger.info("Starting Voice Command Resolution")
    logger.info("=" * 60)

    _, image = take_screenshot()
    logger.info("[Step 1] Captured screenshot")

    children = detect_elements(image)
    logger.info(f"[Step 2] Detected {len(children)} elements")

    hints = get_hints(children)
    logger.info(f"[Step 3] Generated {len(hints)} hints")

    blocks = children_to_blocks(children, hints)
    _current_blocks = blocks
    logger.info(f"[Step 4] Created {len(blocks)} blocks")

    transcript = await transcribe_audio_file(audio_path)
    logger.info(f"[Step 5] Transcribed audio: '{transcript}'")

    command = await plan_command(transcript, blocks)
    logger.info(
        f"[Step 6] Planned command: {command.action} (confidence: {command.confidence})"
    )

    logger.info("=" * 60)
    logger.info("Voice Command Resolution Complete")
    logger.info("=" * 60)

    return ResolveResult(transcript=transcript, command=command, blocks=blocks)

    logger.info("=" * 60)
    logger.info("Voice Command Resolution Complete")
    logger.info("=" * 60)

    return ResolveResult(transcript=transcript, command=command, blocks=blocks)


async def resolve_screenshot_only(screenshot_path: str | None = None) -> ResolveResult:
    """Detect elements from screenshot only (no voice).

    Args:
        screenshot_path: Optional path to screenshot (captures if not provided)

    Returns:
        ResolveResult with blocks
    """
    global _current_blocks

    if screenshot_path:
        image = Image.open(screenshot_path)
    else:
        _, image = take_screenshot()

    children = detect_elements(image)
    hints = get_hints(children)
    blocks = children_to_blocks(children, hints)
    _current_blocks = blocks

    logger.info(f"Detected {len(blocks)} blocks from screenshot")

    return ResolveResult(
        transcript="",
        command=Command(action="noop", confidence=1.0, reason="Screenshot only mode"),
        blocks=blocks,
    )


def on_voice_hotkey():
    """Hotkey handler to capture speech and type it or query AI with screenshot."""
    logging.info("Voice hotkey pressed; recording...")
    try:
        transcript = transcribe_from_mic()
        logging.info(f"Heard: {transcript}")
        print(f"Heard: {transcript}")

        lower = transcript.lower().strip()

        if "ai" in lower:
            query = _extract_ai_query(transcript)
            if query:
                logging.info(f"Querying AI with screenshot: {query}")
                try:
                    _, screenshot = take_screenshot()
                    response = query_openrouter_with_vision(query, screenshot)
                    logging.info(f"AI response: {response}")
                    print(f"AI: {response}")
                    type_text(response)
                except OpenRouterError as e:
                    logging.error(f"AI query failed: {e}")
                    print(f"Error: {e}")
            else:
                logging.info("Heard 'AI' but no query provided")
        else:
            payload = _extract_type_payload(transcript)
            if payload:
                logging.info(f"Typing: {payload}")
                type_text(payload)
            else:
                logging.info("No content to type")
    except ElevenLabsSTTError as e:
        logging.error(f"STT error: {e}")
    except Exception as e:
        logging.error(f"Voice hotkey failed: {e}")


def _extract_ai_query(transcript: str) -> str:
    """Extract AI query from transcript, removing AI-related prefixes.

    Args:
        transcript: User's spoken command

    Returns:
        Clean query string
    """
    text = transcript.strip()

    patterns_to_remove = [
        r"^ai\s*[:]*\s*",
        r"^ask\s+ai\s*[:]*\s*",
        r"^ask\s+the\s+ai\s*[:]*\s*",
    ]

    import re

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()


def _extract_type_payload(transcript: str) -> str:
    """Extract text to type from transcript, removing 'type' prefix if present.

    Args:
        transcript: User's spoken command

    Returns:
        Text to type
    """
    text = transcript.strip()

    if text.lower().startswith("type "):
        return text[5:].strip()

    return text


def start_hotkey_listener():
    """Start global hotkey listeners for element selection and voice typing."""
    import threading

    logging.debug("Setting up hotkeys: E (select) and Ctrl+Alt+V (voice type)")

    def find_keyboard_device():
        """Find the first keyboard event device."""
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            caps = device.capabilities()
            if evdev.ecodes.EV_KEY in caps:
                return device
        return None

    keyboard_device = find_keyboard_device()
    if not keyboard_device:
        logging.error("No keyboard device found")
        return None

    pressed = set()
    running = [True]

    def key_listener():
        """Listen for key events."""
        for event in keyboard_device.read_loop():
            if not running[0]:
                break

            if event.type == evdev.ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                keycode = key_event.keycode

                if event.value == 1:  # Key press
                    pressed.add(keycode)

                    # Single-key trigger for selection (E key)
                    if keycode == "KEY_E":
                        on_hotkey()

                    # Chord trigger for voice typing (Ctrl+Alt+V)
                    ctrl_held = "KEY_LEFTCTRL" in pressed or "KEY_RIGHTCTRL" in pressed
                    alt_held = "KEY_LEFTALT" in pressed or "KEY_RIGHTALT" in pressed
                    if ctrl_held and alt_held and keycode == "KEY_V":
                        on_voice_hotkey()

                elif event.value == 0:  # Key release
                    pressed.discard(keycode)

    # Start listener in a separate thread
    listener_thread = threading.Thread(target=key_listener, daemon=True)
    listener_thread.start()

    # Create a wrapper with stop method
    class ListenerWrapper:
        def __init__(self, thread):
            self.thread = thread

        def stop(self):
            running[0] = False
            keyboard_device.close()

    return ListenerWrapper(listener_thread)


def main():
    """Main entry point."""
    logger.info("Voice Navigation System starting")
    print("\n" + "=" * 60)
    print("  Voice Navigation System")
    print("  Multimodal Hands-Free Interface")
    print("=" * 60)
    print("\nFeatures:")
    print("  • Voice command recognition (Whisper)")
    print("  • UI element detection (OpenCV)")
    print("  • AI command planning")
    print("  • Mouse/keyboard control")
    print("\nUsage:")
    print("  See examples in examples/ directory")
    print("\n")

    logging.info("Voice Navigation System starting")
    print("Voice Navigation System Started")
    print("Press E to enter element selection mode")
    print("Press Ctrl+Alt+V then:")
    print("  - Say '<text>' to type text directly")
    print("  - Say 'AI <query>' to query OpenRouter AI and type the response")
    print("Press Ctrl+C to exit")

    listener = start_hotkey_listener()
    logging.debug("Hotkey listener started")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down...")
        listener.stop()


async def run_demo():
    """Run a demo of the voice navigation system."""
    print("\nRunning Voice Navigation Demo...")

    result = await resolve_screenshot_only()
    if result.blocks:
        blocks = result.blocks
        print(f"\nDetected {len(blocks)} elements")

        print("\nSample blocks:")
        for i, block in enumerate(blocks[:5]):
            print(
                f"  {i + 1}. {block.label} at ({block.x}, {block.y}) - hint: {block.hint}"
            )
    else:
        print("\nNo blocks detected")


if __name__ == "__main__":
    main()
