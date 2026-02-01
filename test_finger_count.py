#!/usr/bin/env python3
"""Test script for finger-count workspace gestures."""

import sys
from pathlib import Path


# Mock finger detection
class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MockHand:
    def __init__(self, fingers_up):
        """Create mock hand with specified fingers up.

        fingers_up: list of 5 booleans [thumb, index, middle, ring, pinky]
        """
        self.lm = [MockLandmark(0.5, 0.5) for _ in range(21)]

        # Set y positions for fingertips to simulate finger up/down
        # Lower y = higher on screen (finger up)
        base_y = 0.5
        up_y = 0.3
        down_y = 0.6

        # Tips: thumb=4, index=8, middle=12, ring=16, pinky=20
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]

        for i, (tip, pip, is_up) in enumerate(zip(tips, pips, fingers_up)):
            if is_up:
                self.lm[tip].y = up_y
                self.lm[pip].y = up_y + 0.1
            else:
                self.lm[tip].y = down_y
                self.lm[pip].y = down_y - 0.05


def count_fingers_mock(hand):
    """Mock version of count_fingers function."""
    lm = hand.lm

    # Check if each finger (excluding thumb) is up
    # Finger is up if tip.y < pip.y and distance is sufficient
    finger_states = []

    # Index (landmarks 5, 6, 8)
    index_up = lm[8].y < lm[6].y
    finger_states.append(index_up)

    # Middle (landmarks 9, 10, 12)
    middle_up = lm[12].y < lm[10].y
    finger_states.append(middle_up)

    # Ring (landmarks 13, 14, 16)
    ring_up = lm[16].y < lm[14].y
    finger_states.append(ring_up)

    # Pinky (landmarks 17, 18, 20)
    pinky_up = lm[20].y < lm[18].y
    finger_states.append(pinky_up)

    return sum(finger_states)


def test_finger_counting():
    """Test finger counting for workspace gestures."""
    print("Testing Finger-Count Workspace Gestures")
    print("=" * 60)

    # Test 1: 1 finger (index only)
    print("\n1. Testing 1 finger (workspace 1):")
    hand1 = MockHand([False, True, False, False, False])
    count = count_fingers_mock(hand1)
    print(f"   Fingers: Index={True}, Middle={False}, Ring={False}, Pinky={False}")
    print(f"   Count: {count}")
    print(f"   Workspace: {count}")
    assert count == 1, "Failed: Expected 1 finger"

    # Test 2: 2 fingers (index + middle)
    print("\n2. Testing 2 fingers (workspace 2):")
    hand2 = MockHand([False, True, True, False, False])
    count = count_fingers_mock(hand2)
    print(f"   Fingers: Index={True}, Middle={True}, Ring={False}, Pinky={False}")
    print(f"   Count: {count}")
    print(f"   Workspace: {count}")
    assert count == 2, "Failed: Expected 2 fingers"

    # Test 3: 3 fingers (index + middle + ring)
    print("\n3. Testing 3 fingers (workspace 3):")
    hand3 = MockHand([False, True, True, True, False])
    count = count_fingers_mock(hand3)
    print(f"   Fingers: Index={True}, Middle={True}, Ring={True}, Pinky={False}")
    print(f"   Count: {count}")
    print(f"   Workspace: {count}")
    assert count == 3, "Failed: Expected 3 fingers"

    # Test 4: 4 fingers (all except thumb)
    print("\n4. Testing 4 fingers (workspace 4):")
    hand4 = MockHand([False, True, True, True, True])
    count = count_fingers_mock(hand4)
    print(f"   Fingers: Index={True}, Middle={True}, Ring={True}, Pinky={True}")
    print(f"   Count: {count}")
    print(f"   Workspace: {count}")
    assert count == 4, "Failed: Expected 4 fingers"

    # Test 5: 0 fingers (fist)
    print("\n5. Testing 0 fingers (no workspace switch):")
    hand5 = MockHand([False, False, False, False, False])
    count = count_fingers_mock(hand5)
    print(f"   Fingers: Index={False}, Middle={False}, Ring={False}, Pinky={False}")
    print(f"   Count: {count}")
    print(f"   Action: No workspace switch (count < 1)")
    assert count == 0, "Failed: Expected 0 fingers"

    # Test 6: Thumb only (should not count)
    print("\n6. Testing thumb only (should not count):")
    hand6 = MockHand([True, False, False, False, False])
    count = count_fingers_mock(hand6)
    print(
        f"   Fingers: Thumb={True}, Index={False}, Middle={False}, Ring={False}, Pinky={False}"
    )
    print(f"   Count: {count} (thumb excluded)")
    print(f"   Action: No workspace switch (thumb doesn't count)")
    assert count == 0, "Failed: Expected 0 fingers (thumb excluded)"

    print("\n" + "=" * 60)
    print("All finger-count tests passed!")
    print("\nNote: Run with actual camera to test real gesture detection")
    print("      python3 current/tracking/hands.py")
    print("\nWorkspace Commands:")
    print("  1 finger → swaymsg workspace number 1")
    print("  2 fingers → swaymsg workspace number 2")
    print("  3 fingers → swaymsg workspace number 3")
    print("  4 fingers → swaymsg workspace number 4")


if __name__ == "__main__":
    test_finger_counting()
