import time
import subprocess
import shutil
from unittest.mock import Mock, patch, MagicMock


class MockLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def dist(a, b):
    return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5


def finger_up(lm, mcp, pip, tip):
    return lm[tip].y < lm[pip].y and dist(lm[mcp], lm[tip]) > 0.05


def thumb_up(lm):
    return lm[4].y < lm[3].y


def is_thumbs_up(lm):
    if not thumb_up(lm):
        return False
    index_up = finger_up(lm, 5, 6, 8)
    middle_down = not finger_up(lm, 9, 10, 12)
    ring_down = not finger_up(lm, 13, 14, 16)
    pinky_down = not finger_up(lm, 17, 18, 20)
    return index_up and middle_down and ring_down and pinky_down


def create_hand_landmarks(thumb_up_val, index_up, middle_up, ring_up, pinky_up):
    lm = []
    for i in range(21):
        lm.append(MockLandmark(i * 0.05, 0.5))
    lm[3].y = 0.4 if thumb_up_val else 0.6
    lm[4].y = 0.3 if thumb_up_val else 0.7
    lm[6].y = 0.4 if index_up else 0.6
    lm[8].y = 0.3 if index_up else 0.7
    lm[10].y = 0.4 if middle_up else 0.6
    lm[12].y = 0.3 if middle_up else 0.7
    lm[14].y = 0.4 if ring_up else 0.6
    lm[16].y = 0.3 if ring_up else 0.7
    lm[18].y = 0.4 if pinky_up else 0.6
    lm[20].y = 0.3 if pinky_up else 0.7
    return lm


print("Testing App Launcher Gesture Detection")
print("=" * 50)

print("\n1. Testing thumb + index gesture (should be True):")
lm = create_hand_landmarks(
    thumb_up_val=True, index_up=True, middle_up=False, ring_up=False, pinky_up=False
)
result = is_thumbs_up(lm)
print(f"   Result: {result}")
assert result == True, "Failed: Thumb + index should be detected"
print("   ✓ PASSED")

print("\n2. Testing all fingers up (should be False):")
lm = create_hand_landmarks(
    thumb_up_val=True, index_up=True, middle_up=True, ring_up=True, pinky_up=True
)
result = is_thumbs_up(lm)
print(f"   Result: {result}")
assert result == False, "Failed: Middle/ring/pinky must be down"
print("   ✓ PASSED")

print("\n3. Testing thumb down (should be False):")
lm = create_hand_landmarks(
    thumb_up_val=False, index_up=True, middle_up=False, ring_up=False, pinky_up=False
)
result = is_thumbs_up(lm)
print(f"   Result: {result}")
assert result == False, "Failed: Thumb down should not trigger"
print("   ✓ PASSED")

print("\n4. Testing index only (workspace 1 gesture - should be False):")
lm = create_hand_landmarks(
    thumb_up_val=False, index_up=True, middle_up=False, ring_up=False, pinky_up=False
)
result = is_thumbs_up(lm)
print(f"   Result: {result}")
assert result == False, "Failed: Index only should not trigger app launcher"
print("   ✓ PASSED")

print("\n5. Testing thumb_up function:")
lm = create_hand_landmarks(
    thumb_up_val=True, index_up=False, middle_up=False, ring_up=False, pinky_up=False
)
result = thumb_up(lm)
print(f"   Thumb up: {result}")
assert result == True, "Failed: thumb_up should return True"
lm = create_hand_landmarks(
    thumb_up_val=False, index_up=False, middle_up=False, ring_up=False, pinky_up=False
)
result = thumb_up(lm)
print(f"   Thumb down: {result}")
assert result == False, "Failed: thumb_up should return False"
print("   ✓ PASSED")


def test_command_execution():
    print("\n6. Testing command execution (mocked):")

    APP_LAUNCHER_AUDIO_START = "paplay /usr/share/sounds/freedesktop/stereo/bell.oga"
    APP_LAUNCHER_AUDIO_STOP = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"

    def play_app_launcher_sound(start_recording=True):
        pass

    def execute_app_launcher_command(command):
        command = command.strip()
        if not command:
            print("No command detected")
            return

        print(f"Processing: {command}")
        executable = shutil.which(command)
        if executable:
            print(f"Found executable: {executable}")
            subprocess.Popen([command], start_new_session=True)
        else:
            url = f"https://duckduckgo.com/?q={command}"
            print(f"Opening search: {url}")
            subprocess.Popen(["xdg-open", url], start_new_session=True)
        play_app_launcher_sound(start_recording=False)

    with patch("subprocess.Popen") as mock_popen:
        with patch("shutil.which", return_value="/usr/bin/firefox"):
            execute_app_launcher_command("firefox")
            mock_popen.assert_called_once_with(["firefox"], start_new_session=True)
            print("   ✓ PASSED: Executable command launched")

    with patch("subprocess.Popen") as mock_popen:
        with patch("shutil.which", return_value=None):
            execute_app_launcher_command("cat videos")
            mock_popen.assert_called_once()
            args = mock_popen.call_args[0][0]
            assert args[0] == "xdg-open"
            assert "cat+videos" in args[1] or "cat videos" in args[1]
            print("   ✓ PASSED: Non-executable opened as search")

    with patch("subprocess.Popen") as mock_popen:
        with patch("shutil.which", return_value=None):
            execute_app_launcher_command("")
            mock_popen.assert_not_called()
            print("   ✓ PASSED: Empty command handled")


test_command_execution()

print("\n" + "=" * 50)
print("All app launcher tests passed!")
print("=" * 50)
