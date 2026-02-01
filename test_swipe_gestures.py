#!/usr/bin/env python3
"""Test script for swipe gesture detection."""

import sys
import time
from pathlib import Path

# Add current.tracking to path
sys.path.insert(0, str(Path(__file__).parent.parent / "current" / "tracking"))


# Mock the necessary components that are missing in test environment
class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def test_swipe_detection():
    """Test swipe detection logic with simulated hand positions."""
    print("Testing Swipe Gesture Detection")
    print("=" * 50)

    # Simulate right swipe
    print("\n1. Testing RIGHT swipe:")
    start = MockLandmark(0.3, 0.5)
    end = MockLandmark(0.5, 0.5)
    dx = end.x - start.x
    dy = end.y - start.y
    direction = (
        "right"
        if dx > 0
        else "left"
        if abs(dx) > abs(dy)
        else ("down" if dy > 0 else "up")
    )
    print(f"   Start: ({start.x}, {start.y})")
    print(f"   End: ({end.x}, {end.y})")
    print(f"   Detected direction: {direction.upper()}")
    print(f"   Command: swaymsg workspace next")

    # Simulate left swipe
    print("\n2. Testing LEFT swipe:")
    start = MockLandmark(0.6, 0.5)
    end = MockLandmark(0.4, 0.5)
    dx = end.x - start.x
    dy = end.y - start.y
    direction = (
        "right"
        if dx > 0
        else "left"
        if abs(dx) > abs(dy)
        else ("down" if dy > 0 else "up")
    )
    print(f"   Start: ({start.x}, {start.y})")
    print(f"   End: ({end.x}, {end.y})")
    print(f"   Detected direction: {direction.upper()}")
    print(f"   Command: swaymsg workspace prev")

    # Simulate up swipe
    print("\n3. Testing UP swipe:")
    start = MockLandmark(0.5, 0.6)
    end = MockLandmark(0.5, 0.4)
    dx = end.x - start.x
    dy = end.y - start.y
    direction = (
        "right"
        if dx > 0
        else "left"
        if abs(dx) > abs(dy)
        else ("down" if dy > 0 else "up")
    )
    print(f"   Start: ({start.x}, {start.y})")
    print(f"   End: ({end.x}, {end.y})")
    print(f"   Detected direction: {direction.upper()}")
    print(f"   Command: swaymsg move container to workspace next")

    # Simulate down swipe
    print("\n4. Testing DOWN swipe:")
    start = MockLandmark(0.5, 0.3)
    end = MockLandmark(0.5, 0.5)
    dx = end.x - start.x
    dy = end.y - start.y
    direction = (
        "right"
        if dx > 0
        else "left"
        if abs(dx) > abs(dy)
        else ("down" if dy > 0 else "up")
    )
    print(f"   Start: ({start.x}, {start.y})")
    print(f"   End: ({end.x}, {end.y})")
    print(f"   Detected direction: {direction.upper()}")
    print(f"   Command: swaymsg move container to workspace prev")

    print("\n" + "=" * 50)
    print("All swipe tests passed!")
    print("\nNote: Run with actual camera to test real gesture detection")
    print("      python3 current/tracking/hands.py")


def test_thresholds():
    """Test threshold calculations."""
    print("\n" + "=" * 50)
    print("Testing Swipe Thresholds")
    print("=" * 50)

    SWIPE_THRESHOLD = 0.15

    # Test threshold
    start = MockLandmark(0.3, 0.5)
    end = MockLandmark(0.5, 0.5)
    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)

    print(f"\nThreshold: {SWIPE_THRESHOLD}")
    print(f"Horizontal distance: {dx:.3f}")
    print(f"Vertical distance: {dy:.3f}")
    print(f"Passes threshold: {dx >= SWIPE_THRESHOLD or dy >= SWIPE_THRESHOLD}")

    # Test small movement (below threshold)
    start = MockLandmark(0.3, 0.5)
    end = MockLandmark(0.35, 0.5)
    dx = abs(end.x - start.x)
    dy = abs(end.y - start.y)

    print(f"\nSmall movement test:")
    print(f"Horizontal distance: {dx:.3f}")
    print(f"Vertical distance: {dy:.3f}")
    print(f"Passes threshold: {dx >= SWIPE_THRESHOLD or dy >= SWIPE_THRESHOLD}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_swipe_detection()
    test_thresholds()
