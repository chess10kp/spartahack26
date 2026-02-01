"""Example: Voice Navigation with ElevenLabs STT.

This example demonstrates how to use ElevenLabs STT for voice commands
that interact with UI elements.
"""

import asyncio
import os
import time

from main import resolve_voice_command, execute_command, take_screenshot
from stt_elevenlabs import transcribe_from_mic, ElevenLabsSTTError
from schemas import Block


async def demo_voice_command():
    """Demonstrate voice command processing."""
    print("\n" + "=" * 60)
    print("  Voice Navigation Demo - ElevenLabs STT")
    print("=" * 60)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("\n⚠ ERROR: ELEVENLABS_API_KEY not set")
        print("  Set it with: export ELEVENLABS_API_KEY=your_api_key")
        return

    print("\nSteps:")
    print("  1. Take a screenshot")
    print("  2. Detect UI elements")
    print("  3. Record your voice command")
    print("  4. Transcribe using ElevenLabs STT")
    print("  5. Plan and execute the command")
    print("\nVoice command examples:")
    print('  "Click the submit button"')
    print('  "Double-click the file"')
    print('  "Scroll down"')
    print('  "Type hello world"')

    input("\nPress Enter to start...")

    print("\n[Step 1] Taking screenshot...")
    screenshot_path, screenshot = take_screenshot()
    print(f"  ✓ Screenshot saved: {screenshot_path}")

    print("\n[Step 2] Detecting UI elements...")
    from element_selector import detect_elements
    from child import Child

    children = detect_elements(screenshot)
    print(f"  ✓ Detected {len(children)} UI elements")

    print("\n[Step 3] Recording voice command...")
    print("  Please speak your command (4 seconds)...")

    try:
        temp_file = stt_elevenlabs.record_microphone(duration_sec=4)
        print("  ✓ Recording complete")

        print("\n[Step 4] Transcribing with ElevenLabs STT...")
        transcript = stt_elevenlabs.transcribe_file(temp_file, api_key=api_key)
        print(f"  ✓ Transcript: '{transcript}'")

        os.remove(temp_file)

        print("\n[Step 5] Planning command...")
        from planner import plan_command
        from schemas import Block
        import uuid

        blocks = []
        hints = {}
        for i, child in enumerate(children):
            hint_key = str(i)
            hints[hint_key] = child
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

        command = await plan_command(transcript, blocks)
        print(f"  ✓ Planned action: {command.action}")
        print(f"    Confidence: {command.confidence:.2f}")

        if command.target:
            print(f"    Target: {command.target}")

        print("\n[Step 6] Executing command...")
        await execute_command(command)
        print("  ✓ Command executed")

        print("\n" + "=" * 60)
        print("  Demo Complete!")
        print("=" * 60)

    except ElevenLabsSTTError as e:
        print(f"\n✗ ElevenLabs STT Error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()


async def demo_simple_transcription():
    """Demonstrate simple voice transcription."""
    print("\n" + "=" * 60)
    print("  Simple Transcription Demo - ElevenLabs STT")
    print("=" * 60)

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("\n⚠ ERROR: ELEVENLABS_API_KEY not set")
        print("  Set it with: export ELEVENLABS_API_KEY=your_api_key")
        return

    print("\nSpeak something (4 seconds)...")
    print("Examples:")
    print('  "Hello world"')
    print('  "Click the button"')
    print('  "Type my email"')

    input("\nPress Enter and start speaking...")

    try:
        transcript = transcribe_from_mic(duration_sec=4, api_key=api_key)
        print(f"\n✓ Transcription: '{transcript}'")
    except ElevenLabsSTTError as e:
        print(f"\n✗ ElevenLabs STT Error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def main():
    """Run the demo."""
    print("\nChoose demo:")
    print("  1. Simple transcription")
    print("  2. Full voice navigation")

    choice = input("\nEnter choice (1-2): ").strip()

    if choice == "1":
        await demo_simple_transcription()
    elif choice == "2":
        await demo_voice_command()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    import stt_elevenlabs

    asyncio.run(main())
