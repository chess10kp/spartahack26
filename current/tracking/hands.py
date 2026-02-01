import cv2
import numpy as np
import pyautogui
import time
import sys
from pathlib import Path

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

# =========================
# CONFIG
# =========================
pyautogui.FAILSAFE = False

LEFT_CLOSE_THRESHOLD = 0.045

PINCH_THRESHOLD = 0.035
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
HAND_MODEL_PATH = Path(__file__).parent.parent.parent / "eye_tracking" / "hand_landmarker.task"

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
def handle_voice_command():
    """Record from mic and process voice command."""
    print("Recording voice command...")
    try:
        transcript = transcribe_from_mic()
        print(f"Heard: {transcript}")
        
        lower = transcript.lower().strip()
        if lower.startswith("type "):
            payload = transcript[5:]
            print(f"Typing: {payload}")
            type_text(payload)
        elif lower == "type":
            print("Heard bare 'type' with no content; ignoring")
        else:
            print(f"Voice command: {transcript}")
    except ElevenLabsSTTError as e:
        print(f"STT error: {e}")
    except Exception as e:
        print(f"Voice command failed: {e}")

# =========================
# LEFT HAND CURSOR CONTROL
# =========================
def move_mouse_cartesian(lm):
    global smoothed_dir

    # HARD CLUTCH
    if left_hand_closed(lm):
        return  # no smoothing, no movement, no decay

    origin = lm[5]  # INDEX_MCP
    tip = lm[8]     # INDEX_TIP

    dx = tip.x - origin.x
    dy = tip.y - origin.y

    direction = np.array([dx, dy])
    mag = np.linalg.norm(direction)

    if mag < DEADZONE:
        return

    direction /= mag

    smoothed_dir = (
        smoothed_dir * (1 - SMOOTHING_ALPHA)
        + direction * SMOOTHING_ALPHA
    )

    gain = BASE_GAIN + (MAX_GAIN - BASE_GAIN) * min(mag * 4, 1.0)

    pyautogui.moveRel(
        smoothed_dir[0] * gain,
        smoothed_dir[1] * gain
    )

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
        for hand_lm, handedness in zip(
            results.hand_landmarks,
            results.handedness
        ):
            lm = hand_lm
            label = handedness[0].category_name

            color = (0, 255, 0) if label == "Left" else (0, 0, 255)

            # Draw landmarks manually (no mp_draw in Tasks API)
            for i, p in enumerate(lm):
                x, y = int(p.x * w), int(p.y * h)
                cv2.circle(frame, (x, y), 3, color, -1)
                cv2.putText(frame, str(i), (x + 4, y - 4),
                            FONT, 0.35, (255, 255, 0), 1)
            
            # Draw connections
            connections = [
                (0,1),(1,2),(2,3),(3,4),  # thumb
                (0,5),(5,6),(6,7),(7,8),  # index
                (0,9),(9,10),(10,11),(11,12),  # middle
                (0,13),(13,14),(14,15),(15,16),  # ring
                (0,17),(17,18),(18,19),(19,20),  # pinky
                (5,9),(9,13),(13,17)  # palm
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

    # Trigger voice command when voice mode is activated
    if vm and not prev_vm:
        handle_voice_command()
        vm = False  # Reset after handling
    prev_vm = vm

    # Process nose tracking if eye mode is active
    if em:
        frame = nose_tracker.process_frame(frame)

    # =========================
    # UI OVERLAY
    # =========================
    vm_color = (0, 255, 0) if vm else (0, 0, 255)
    em_color = (0, 255, 0) if em else (0, 0, 255)

    cv2.putText(frame, f"VOICE MODE (1): {vm}", (10, 30),
                FONT, 0.7, vm_color, 2)
    cv2.putText(frame, f"EYE MODE (2): {em}", (10, 60),
                FONT, 0.7, em_color, 2)

    for i, g in enumerate(["ONE", "TWO"]):
        if gesture_start[g]:
            remaining = max(0, HOLD_TIME - (now - gesture_start[g]))
            cv2.putText(frame, f"{g} HOLD: {remaining:.1f}s",
                        (10, 100 + i * 25),
                        FONT, 0.6, (255, 255, 0), 2)

    cv2.imshow("Gesture Control Pipeline", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

nose_tracker.stop()
cap.release()
cv2.destroyAllWindows()
