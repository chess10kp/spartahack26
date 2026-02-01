import cv2
import numpy as np
import pyautogui
import time
import sys
import threading
import os
import subprocess
from pathlib import Path

os.environ["QT_LOGGING_RULES"] = "qt.qpa.font.debug=false"

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
from element_selector import capture_screen, detect_elements, get_hints
from child import Child

# =========================
# CONFIG
# =========================
pyautogui.FAILSAFE = False

LEFT_CLOSE_THRESHOLD = 0.045

PINCH_THRESHOLD = 0.05
DOUBLE_CLICK_WINDOW = 0.35

HOLD_TIME = 0.5  # Reduced for easier activation

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

# Voice mode with hints state
voice_mode_active = False
current_hints = {}  # hint -> Child mapping


# =========================
# HELPERS
# =========================
def dist(a, b):
    return np.linalg.norm([a.x - b.x, a.y - b.y])


def finger_up(lm, mcp, pip, tip):
    return lm[tip].y < lm[pip].y and dist(lm[mcp], lm[tip]) > 0.05


def left_hand_closed(lm):
    return dist(lm[5], lm[8]) < LEFT_CLOSE_THRESHOLD


# =========================
# VOICE COMMAND HANDLER
# =========================
def voice_record_thread():
    """Background thread to record and transcribe voice."""
    global voice_recording, voice_result
    try:
        transcript = transcribe_from_mic()
        voice_result = ("success", transcript)
    except ElevenLabsSTTError as e:
        voice_result = ("error", str(e))
    except Exception as e:
        voice_result = ("error", str(e))
    voice_recording = False


def start_voice_mode():
    """Start voice mode: capture screen, detect elements, show overlay, record."""
    global \
        voice_mode_active, \
        current_hints, \
        voice_recording, \
        voice_result, \
        voice_start_time

    print("Starting voice mode...")

    # Capture screenshot and detect elements
    screenshot = capture_screen()
    children = detect_elements(screenshot)

    if not children:
        print("No UI elements detected")
        return

    current_hints = get_hints(children)
    print(f"Detected {len(current_hints)} elements with hints")

    # Start voice recording in background
    voice_recording = True
    voice_result = None
    voice_start_time = time.time()
    voice_mode_active = True

    # Create overlay image BEFORE starting threads (so hints are captured)
    global hints_overlay_img
    hints_overlay_img = create_hints_overlay_image()
    
    # Start recording thread
    thread = threading.Thread(target=voice_record_thread, daemon=True)
    thread.start()

    # Show overlay (runs in separate thread to not block main loop)
    overlay_thread = threading.Thread(target=show_hints_overlay, daemon=True)
    overlay_thread.start()

    print("Recording voice command... Speak: <hint> <action>")


def create_hints_overlay_image():
    """Create a screenshot with hints overlaid, returns the image."""
    global current_hints

    from PIL import ImageGrab

    screenshot = ImageGrab.grab()

    # Convert to OpenCV format
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    print(f"[DEBUG] Drawing {len(current_hints)} hints on overlay (img size: {img.shape})")

    # Draw hints on the image
    for hint_text, child in current_hints.items():
        x = int(child.absolute_position[0] + child.width / 2)
        y = int(child.absolute_position[1] + child.height / 2)

        print(f"[DEBUG]   Hint '{hint_text}' at ({x}, {y})")

        text = hint_text.upper()
        (text_w, text_h), baseline = cv2.getTextSize(text, FONT, 1.2, 2)

        padding = 10
        # Black border
        cv2.rectangle(
            img,
            (x - text_w // 2 - padding - 2, y - text_h // 2 - padding - 2),
            (x + text_w // 2 + padding + 2, y + text_h // 2 + padding + 2),
            (0, 0, 0),
            -1,
        )
        # Red background
        cv2.rectangle(
            img,
            (x - text_w // 2 - padding, y - text_h // 2 - padding),
            (x + text_w // 2 + padding, y + text_h // 2 + padding),
            (0, 0, 220),
            -1,
        )

        cv2.putText(
            img, text, (x - text_w // 2, y + text_h // 2), FONT, 1.2, (255, 255, 255), 2
        )

    return img


# Global for overlay
hints_overlay_img = None
hints_window_name = "Voice Mode - Speak: <hint> <action>"


def show_hints_overlay():
    """Show fullscreen overlay with hints using OpenCV."""
    global hints_overlay_img, voice_recording

    # hints_overlay_img is already created in start_voice_mode()

    # Create fullscreen window
    cv2.namedWindow(hints_window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        hints_window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
    )

    # Show overlay while recording
    while voice_recording:
        # Add recording indicator
        display_img = hints_overlay_img.copy()
        h, w = display_img.shape[:2]

        elapsed = time.time() - voice_start_time
        remaining = max(0, VOICE_RECORD_DURATION - elapsed)

        # Recording banner at top
        cv2.rectangle(display_img, (0, 0), (w, 60), (0, 0, 150), -1)
        pulse = int(127 + 127 * np.sin(elapsed * 6))
        cv2.circle(display_img, (40, 30), 15, (0, 0, pulse + 128), -1)
        cv2.putText(
            display_img,
            f"RECORDING... {remaining:.1f}s  |  Speak: <hint> <action>",
            (70, 40),
            FONT,
            1.0,
            (255, 255, 255),
            2,
        )

        cv2.imshow(hints_window_name, display_img)
        if cv2.waitKey(30) & 0xFF == 27:  # ESC to cancel
            break

    cv2.destroyWindow(hints_window_name)
    hints_overlay_img = None


def parse_hint_and_action(transcript: str) -> tuple:
    """Parse transcript to extract hint and action.

    Returns: (hint, action, extra_text)
    """
    words = transcript.lower().strip().split()

    if not words:
        return None, None, None

    hint = words[0] if words else None
    action = None
    extra_text = None

    if len(words) >= 2:
        rest = " ".join(words[1:])

        if rest.startswith("click") or rest == "click":
            action = "click"
        elif rest.startswith("double click"):
            action = "double_click"
        elif rest.startswith("right click"):
            action = "right_click"
        elif rest.startswith("type "):
            action = "type"
            extra_text = rest[5:]
        else:
            action = "query"
            extra_text = rest
    elif len(words) == 1:
        action = "click"

    return hint, action, extra_text


def execute_voice_command(hint: str, action: str, extra_text: str):
    """Execute the parsed voice command."""
    global current_hints

    if hint not in current_hints:
        print(f"Hint '{hint}' not found in detected elements")
        return

    child = current_hints[hint]
    center_x = int(child.absolute_position[0] + child.width / 2)
    center_y = int(child.absolute_position[1] + child.height / 2)

    print(f"Executing: {action} on hint '{hint}' at ({center_x}, {center_y})")

    if action == "click":
        pyautogui.click(center_x, center_y)
    elif action == "double_click":
        pyautogui.doubleClick(center_x, center_y)
    elif action == "right_click":
        pyautogui.rightClick(center_x, center_y)
    elif action == "type":
        pyautogui.click(center_x, center_y)
        time.sleep(0.1)
        type_text(extra_text)
    elif action == "query":
        pyautogui.click(center_x, center_y)
        time.sleep(0.1)
        response = query_ai(extra_text)
        if response:
            type_text(response)


def query_ai(prompt: str) -> str:
    """Query AI for a response to type."""
    import os

    try:
        import openai

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY not set, echoing prompt")
            return prompt

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Provide concise, direct responses suitable for typing into a text field. No explanations, just the answer.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        print("openai package not installed, echoing prompt")
        return prompt
    except Exception as e:
        print(f"AI query failed: {e}")
        return prompt


def process_voice_result():
    """Process completed voice transcription."""
    global voice_result, voice_mode_active, current_hints

    if voice_result is None:
        return

    status, data = voice_result
    voice_result = None
    voice_mode_active = False

    if status == "error":
        print(f"Voice command failed: {data}")
        return

    transcript = data
    print(f"Heard: {transcript}")

    hint, action, extra_text = parse_hint_and_action(transcript)

    if hint and action:
        execute_voice_command(hint, action, extra_text)
    else:
        print(f"Could not parse command: {transcript}")

    current_hints = {}


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
# MAIN LOOP
# =========================
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
                cv2.putText(frame, str(i), (x + 4, y - 4), FONT, 0.35, (255, 255, 0), 1)

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

    if gesture_start["TWO"] and now - gesture_start["TWO"] >= HOLD_TIME:
        em = not em
        if em:
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

    for i, g in enumerate(["ONE", "TWO"]):
        if gesture_start[g]:
            remaining = max(0, HOLD_TIME - (now - gesture_start[g]))
            cv2.putText(
                frame,
                f"{g} HOLD: {remaining:.1f}s",
                (10, 100 + i * 25),
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

    cv2.imshow("Gesture Control Pipeline", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

nose_tracker.stop()
cap.release()
cv2.destroyAllWindows()
