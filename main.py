import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "voice_nav"))

from current.tracking.hands import run_tracking
from voice_nav.main import trigger_element_selection


def main():
    print("Multimodal Hands-Free Interface")
    print("Thumbs-up to enter voice mode, thumb closes to exit")
    print("Press ESC to quit\n")

    def on_voice_trigger():
        print("\n[Voice Mode] Thumbs-up detected, entering element selection...")
        trigger_element_selection()
        print("[Voice Mode] Exited")

    run_tracking(trigger_voice_mode=on_voice_trigger)


if __name__ == "__main__":
    main()
