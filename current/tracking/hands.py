import cv2
import numpy as np
import pyautogui
import time
import sys
import threading
import os
import subprocess
from pathlib import Path

os.environ["QT_LOGGING_RULES"] = "qt.qpa.font.debug=false;qt.qpa.*=false"


class QtWarningFilter:
    def __init__(self):
        self.original_stderr = (
            sys.__stderr__ if hasattr(sys, "__stderr__") else sys.stderr
        )

    def write(self, text):
        if "QFont::setPointSizeF" not in text and "qt.qpa" not in text.lower():
            if self.original_stderr:
                self.original_stderr.write(text)

    def flush(self):
        if self.original_stderr:
            self.original_stderr.flush()


if hasattr(sys, "__stderr__") and sys.__stderr__:
    sys.stderr = QtWarningFilter()

import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

# Add eye_tracking to path for nose tracker import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "eye_tracking"))
from nose_tracker import NoseTracker

# Add voice_nav to path for voice control
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "voice_nav"))
from stt_elevenlabs import transcribe_from_mic, ElevenLabsSTTError
from typing_control import type_text
from element_selector import capture_screen
from ai_client import query_openrouter_with_vision, OpenRouterError

# =========================
# CONFIG
# =========================
pyautogui.FAILSAFE = False

LEFT_CLOSE_THRESHOLD = 0.045

PINCH_THRESHOLD = 0.05
DOUBLE_CLICK_WINDOW = 0.35

HOLD_TIME = 0.5  # For ONE gesture
TWO_TRIGGER_TIME = 0.1  # For TWO gesture (nose mode)

BASE_GAIN = 35
MAX_GAIN = 120
SMOOTHING_ALPHA = 0.3
DEADZONE = 0.005

FONT = cv2.FONT_HERSHEY_SIMPLEX

# =========================
# MEDIAPIPE HAND LANDMARKER (Tasks API)
# =========================
HAND_MODEL_PATH = (
    Path(__file__).parent.parent.parent / "eye_tracking" / "hand_landmarker.task"
)

hand_options = vision.HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=str(HAND_MODEL_PATH)),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)

# =========================
# STATE
# =========================
smoothed_dir = np.array([0.0, 0.0])

vm = False
em = False
prev_em = False  # Track previous state to detect changes
prev_vm = False  # Track previous voice mode state

gesture_start = {"ONE": None, "TWO": None}

# Nose tracker instance
nose_tracker = NoseTracker()

last_pinch_time = 0.0
pinch_active = False

# Voice recording state
voice_recording = False
voice_result = None
voice_start_time = 0.0
VOICE_RECORD_DURATION = 4.0  # matches DEFAULT_DURATION_SEC in stt_elevenlabs

# Voice mode state
voice_mode_active = False

# Workspace gesture state
last_workspace_switch_time = 0.0
current_finger_count = 0


# =========================
# HELPERS
# =========================
def dist(a, b):
    return np.linalg.norm([a.x - b.x, a.y - b.y])


def finger_up(lm, mcp, pip, tip):
    return lm[tip].y < lm[pip].y and dist(lm[mcp], lm[tip]) > 0.05


def left_hand_closed(lm):
    return dist(lm[5], lm[8]) < LEFT_CLOSE_THRESHOLD


def thumb_up(lm):
    return lm[4].y < lm[3].y


# =========================
# VOICE COMMAND HANDLER
# =========================
def voice_record_thread():
    """Background thread to record and transcribe voice."""
    global voice_recording, voice_result
    try:
        transcript = transcribe_from_mic()
        voice_result = ("success", transcript)
        print(f"[Voice Mode] Transcription successful: {transcript}")
    except ElevenLabsSTTError as e:
        voice_result = ("error", str(e))
        print(f"[Voice Mode] ElevenLabs STT Error: {e}")
    except Exception as e:
        voice_result = ("error", str(e))
        print(f"[Voice Mode] Unexpected error: {e}")
        import traceback

        traceback.print_exc()
    voice_recording = False


def start_voice_mode():
    """Start voice mode: record speech and type directly or query AI with screenshot."""
    global voice_mode_active, voice_recording, voice_result, voice_start_time

    print("Starting voice mode (direct input)...")

    voice_recording = True
    voice_result = None
    voice_start_time = time.time()
    voice_mode_active = True

    thread = threading.Thread(target=voice_record_thread, daemon=True)
    thread.start()

    print("Recording... speak now")


def process_voice_result():
    """Process completed voice transcription: type directly or query AI."""
    global voice_result, voice_mode_active

    if voice_result is None:
        return

    status, data = voice_result
    voice_result = None
    voice_mode_active = False

    if status == "error":
        print(f"Voice command failed: {data}")
        return

    transcript = data.strip()
    print(f"Heard: {transcript}")

    if not transcript:
        print("No speech detected")
        return

    lower = transcript.lower()

    if "ai" in lower:
        query = _extract_ai_query(transcript)
        if query:
            print(f"Querying AI with screenshot: {query}")
            try:
                screenshot = capture_screen()
                response = query_openrouter_with_vision(query, screenshot)
                print(f"AI response: {response}")
                type_text(response)
            except OpenRouterError as e:
                print(f"AI query failed: {e}")
        else:
            print("Heard 'AI' but no query provided")
    else:
        print(f"Typing: {transcript}")
        type_text(transcript)


def _extract_ai_query(transcript: str) -> str:
    """Extract AI query from transcript, removing AI-related prefixes."""
    import re

    text = transcript.strip()
    patterns_to_remove = [
        r"^ai\s*[:]*\s*",
        r"^ask\s+ai\s*[:]*\s*",
        r"^ask\s+the\s+ai\s*[:]*\s*",
    ]
    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip()


# =========================
# APP LAUNCHER GESTURE
# =========================
def play_app_launcher_sound(start_recording=True):
    try:
        if start_recording:
            subprocess.run(APP_LAUNCHER_AUDIO_START.split(), check=False, timeout=1)
        else:
            subprocess.run(APP_LAUNCHER_AUDIO_STOP.split(), check=False, timeout=1)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


def app_launcher_record_thread():
    global app_launcher_recording, app_launcher_voice_result
    try:
        print("[App Launcher] Starting transcription...")
        transcript = transcribe_from_mic(duration_sec=APP_LAUNCHER_RECORD_DURATION)
        app_launcher_voice_result = ("success", transcript)
        print(f"[App Launcher] Transcription successful: {transcript}")
    except ElevenLabsSTTError as e:
        app_launcher_voice_result = ("error", str(e))
        print(f"[App Launcher] ElevenLabs STT Error: {e}")
    except Exception as e:
        app_launcher_voice_result = ("error", str(e))
        print(f"[App Launcher] Unexpected error: {e}")
        import traceback

        traceback.print_exc()
    app_launcher_recording = False


def start_app_launcher():
    global \
        app_launcher_active, \
        app_launcher_recording, \
        app_launcher_voice_result, \
        app_launcher_voice_start_time
    print("Starting app launcher... Speak app name!")
    play_app_launcher_sound(start_recording=True)
    app_launcher_recording = True
    app_launcher_voice_result = None
    app_launcher_voice_start_time = time.time()
    app_launcher_active = True
    thread = threading.Thread(target=app_launcher_record_thread, daemon=True)
    thread.start()


def execute_app_launcher_command(command):
    import shutil

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


def process_app_launcher_result():
    global app_launcher_voice_result, app_launcher_active
    if app_launcher_voice_result is None:
        return
    status, data = app_launcher_voice_result
    app_launcher_voice_result = None
    app_launcher_active = False

    if status == "error":
        print(f"App launcher voice failed: {data}")
        play_app_launcher_sound(start_recording=False)
        return

    transcript = data
    print(f"App launcher heard: {transcript}")
    execute_app_launcher_command(transcript)


# =========================
# LEFT HAND CURSOR CONTROL
# =========================
def move_mouse_cartesian(lm):
    global smoothed_dir

    # HARD CLUTCH
    if left_hand_closed(lm):
        return  # no smoothing, no movement, no decay

    origin = lm[5]  # INDEX_MCP
    tip = lm[8]  # INDEX_TIP

    dx = tip.x - origin.x
    dy = tip.y - origin.y

    direction = np.array([dx, dy])
    mag = np.linalg.norm(direction)

    if mag < DEADZONE:
        return

    direction /= mag

    smoothed_dir = smoothed_dir * (1 - SMOOTHING_ALPHA) + direction * SMOOTHING_ALPHA

    gain = BASE_GAIN + (MAX_GAIN - BASE_GAIN) * min(mag * 4, 1.0)

    pyautogui.moveRel(smoothed_dir[0] * gain, smoothed_dir[1] * gain)


# =========================
# RIGHT HAND: PINCH CLICKS
# =========================
def handle_pinch_clicks(lm):
    global last_pinch_time, pinch_active

    pinch_dist = dist(lm[4], lm[8])
    now = time.time()

    if pinch_dist < PINCH_THRESHOLD and not pinch_active:
        pinch_active = True

        if now - last_pinch_time < DOUBLE_CLICK_WINDOW:
            pyautogui.rightClick()
            last_pinch_time = 0.0
        else:
            pyautogui.click()
            last_pinch_time = now

    if pinch_dist >= PINCH_THRESHOLD:
        pinch_active = False


# =========================
# RIGHT HAND: MODE GESTURES
# =========================
def detect_right_gesture(lm):
    index = finger_up(lm, 5, 6, 8)
    middle = finger_up(lm, 9, 10, 12)
    ring = finger_up(lm, 13, 14, 16)
    pinky = finger_up(lm, 17, 18, 20)

    if index and not middle and not ring and not pinky:
        return "ONE"

    if index and middle and not ring and not pinky:
        if lm[12].x > lm[8].x:
            return "TWO"

    return None


# =========================
# LEFT HAND WORKSPACE GESTURES
# =========================
def count_fingers(lm):
    """Count number of fingers extended on a hand.

    Returns: Integer from 0-5 representing number of fingers up.
    """
    index = finger_up(lm, 5, 6, 8)
    middle = finger_up(lm, 9, 10, 12)
    ring = finger_up(lm, 13, 14, 16)
    pinky = finger_up(lm, 17, 18, 20)

    count = 0
    if index:
        count += 1
    if middle:
        count += 1
    if ring:
        count += 1
    if pinky:
        count += 1

    return count


def handle_workspace_switch(finger_count):
    """Switch to workspace based on finger count.

    Args:
        finger_count: Number of fingers (1-4)
    """
    global last_workspace_switch_time

    now = time.time()
    if now - last_workspace_switch_time < 0.5:
        return

    if finger_count < 1 or finger_count > 4:
        return

    workspace_num = finger_count
    print(f"Switching to workspace {workspace_num}")
    subprocess.run(["swaymsg", "workspace", "number", str(workspace_num)], check=False)

    last_workspace_switch_time = now


# =========================
# MAIN LOOP
# =========================
def run_tracking(trigger_voice_mode=None):
    """Main tracking loop.

    Args:
        trigger_voice_mode: Optional callback for voice mode trigger (unused, kept for API compat)
    """
    global vm, em, prev_em, prev_vm, gesture_start, smoothed_dir
    global \
        last_pinch_time, \
        pinch_active, \
        voice_recording, \
        voice_result, \
        voice_start_time
    global voice_mode_active, current_hints, hints_overlay_img, current_finger_count
    global \
        app_launcher_active, \
        app_launcher_recording, \
        app_launcher_voice_result, \
        app_launcher_voice_start_time
    global app_launcher_gesture_start, last_app_launcher_time

    cap = cv2.VideoCapture(1)
    print("FINAL gesture pipeline running (ESC to quit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        now = time.time()

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int(time.time() * 1000)
        results = hand_landmarker.detect_for_video(mp_image, timestamp_ms)

        current_gesture = None

        if results.hand_landmarks and results.handedness:
            for hand_lm, handedness in zip(results.hand_landmarks, results.handedness):
                lm = hand_lm
                label = handedness[0].category_name

                color = (0, 255, 0) if label == "Left" else (0, 0, 255)

                # Draw landmarks manually (no mp_draw in Tasks API)
                for i, p in enumerate(lm):
                    x, y = int(p.x * w), int(p.y * h)
                    cv2.circle(frame, (x, y), 3, color, -1)
                    cv2.putText(
                        frame, str(i), (x + 4, y - 4), FONT, 0.35, (255, 255, 0), 1
                    )

                # Draw connections
                connections = [
                    (0, 1),
                    (1, 2),
                    (2, 3),
                    (3, 4),  # thumb
                    (0, 5),
                    (5, 6),
                    (6, 7),
                    (7, 8),  # index
                    (0, 9),
                    (9, 10),
                    (10, 11),
                    (11, 12),  # middle
                    (0, 13),
                    (13, 14),
                    (14, 15),
                    (15, 16),  # ring
                    (0, 17),
                    (17, 18),
                    (18, 19),
                    (19, 20),  # pinky
                    (5, 9),
                    (9, 13),
                    (13, 17),  # palm
                ]
                for c1, c2 in connections:
                    p1 = (int(lm[c1].x * w), int(lm[c1].y * h))
                    p2 = (int(lm[c2].x * w), int(lm[c2].y * h))
                    cv2.line(frame, p1, p2, (200, 200, 200), 2)

                # Note: With flipped camera, "Left" in MediaPipe = your right hand
                # So we check for "Left" label to detect right hand gestures
                if label == "Left":
                    handle_pinch_clicks(lm)
                    current_gesture = detect_right_gesture(lm)
                    if current_gesture:
                        print(f"Detected gesture: {current_gesture}")

                # Workspace switching and app launcher use LEFT HAND only
                # Note: With flipped camera, "Right" in MediaPipe = your left hand
                if label == "Right":
                    finger_count = count_fingers(lm)
                    if finger_count > 0:
                        handle_workspace_switch(finger_count)
                    current_finger_count = finger_count

                    # App launcher gesture (thumbs up)
                    if is_thumbs_up(lm):
                        if app_launcher_gesture_start is None:
                            app_launcher_gesture_start = now
                        elif now - app_launcher_gesture_start >= APP_LAUNCHER_HOLD_TIME:
                            if now - last_app_launcher_time >= APP_LAUNCHER_DEBOUNCE:
                                if not app_launcher_recording:
                                    start_app_launcher()
                                    last_app_launcher_time = now
                                app_launcher_gesture_start = None
                    else:
                        app_launcher_gesture_start = None

                # Reset state when right hand (MediaPipe "Left") is detected
                if label == "Left":
                    current_finger_count = 0
                    app_launcher_gesture_start = None

        # =========================
        # MODE STATE MACHINE
        # =========================
        for g in ["ONE", "TWO"]:
            if current_gesture == g:
                if gesture_start[g] is None:
                    gesture_start[g] = now
            else:
                gesture_start[g] = None

        if gesture_start["ONE"] and now - gesture_start["ONE"] >= HOLD_TIME:
            vm = not vm
            if vm:
                em = False
            gesture_start["ONE"] = None

        if gesture_start["TWO"] and now - gesture_start["TWO"] >= TWO_TRIGGER_TIME:
            em = True
            vm = False
            gesture_start["TWO"] = None

        # Start/stop nose tracker when eye mode changes
        if em and not prev_em:
            nose_tracker.start()
        elif not em and prev_em:
            nose_tracker.stop()
        prev_em = em

        # Trigger voice mode when activated (screenshot + hints + recording)
        if vm and not prev_vm and not voice_recording:
            start_voice_mode()
            vm = False  # Reset after starting
        prev_vm = vm

        # Check for completed voice transcription
        if voice_result is not None:
            process_voice_result()

        # Check for completed app launcher voice transcription
        if app_launcher_voice_result is not None:
            process_app_launcher_result()

        # Process nose tracking if eye mode is active
        if em:
            frame, double_blink = nose_tracker.process_frame(frame)
            if double_blink:
                # Double blink detected - click and exit eye mode
                subprocess.run(["ydotool", "click", "0xC0"])
                print("Double blink detected - clicked and exiting eye mode")
                em = False
                nose_tracker.stop()

        # =========================
        # UI OVERLAY
        # =========================
        vm_color = (0, 255, 0) if vm else (0, 0, 255)
        em_color = (0, 255, 0) if em else (0, 0, 255)

        cv2.putText(frame, f"VOICE MODE (1): {vm}", (10, 30), FONT, 0.7, vm_color, 2)
        cv2.putText(frame, f"EYE MODE (2): {em}", (10, 60), FONT, 0.7, em_color, 2)

        # Workspace finger count display
        if current_finger_count > 0:
            cv2.putText(
                frame,
                f"WORKSPACE: {current_finger_count}",
                (10, 90),
                FONT,
                0.8,
                (0, 255, 255),
                2,
            )

        for i, g in enumerate(["ONE", "TWO"]):
            if gesture_start[g]:
                hold_time = HOLD_TIME if g == "ONE" else TWO_TRIGGER_TIME
                remaining = max(0, hold_time - (now - gesture_start[g]))
                cv2.putText(
                    frame,
                    f"{g} HOLD: {remaining:.2f}s",
                    (10, 120 + i * 25),
                    FONT,
                    0.6,
                    (255, 255, 0),
                    2,
                )

        # Voice recording overlay
        if voice_recording:
            elapsed = now - voice_start_time
            remaining = max(0, VOICE_RECORD_DURATION - elapsed)

            # Semi-transparent red overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 150), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

            # Recording indicator with pulsing dot
            pulse = int(127 + 127 * np.sin(elapsed * 6))
            cv2.circle(frame, (30, 40), 12, (0, 0, pulse + 128), -1)
            cv2.putText(
                frame,
                f"RECORDING... {remaining:.1f}s",
                (50, 50),
                FONT,
                1.0,
                (255, 255, 255),
                2,
            )
            cv2.putText(frame, "Speak now!", (50, 75), FONT, 0.6, (200, 200, 255), 1)

        # App launcher recording overlay
        if app_launcher_recording:
            elapsed = now - app_launcher_voice_start_time
            remaining = max(0, APP_LAUNCHER_RECORD_DURATION - elapsed)

            # Semi-transparent blue overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 150), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

            # Recording indicator with pulsing dot
            pulse = int(127 + 127 * np.sin(elapsed * 6))
            cv2.circle(frame, (30, 40), 12, (0, 0, pulse + 128), -1)
            cv2.putText(
                frame,
                f"APP LAUNCHER... {remaining:.1f}s",
                (50, 50),
                FONT,
                1.0,
                (255, 255, 255),
                2,
            )
            cv2.putText(
                frame, "Speak app name!", (50, 75), FONT, 0.6, (200, 200, 255), 1
            )

        # App launcher gesture hold progress
        if app_launcher_gesture_start:
            remaining = max(
                0, APP_LAUNCHER_HOLD_TIME - (now - app_launcher_gesture_start)
            )
            cv2.putText(
                frame,
                f"APP LAUNCHER: {remaining:.2f}s",
                (10, 145),
                FONT,
                0.6,
                (255, 165, 0),
                2,
            )

        cv2.imshow("Gesture Control Pipeline", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    nose_tracker.stop()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_tracking()
