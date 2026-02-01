import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time

# =========================
# CONFIG
# =========================
pyautogui.FAILSAFE = False

LEFT_CLOSE_THRESHOLD = 0.045

PINCH_THRESHOLD = 0.035
DOUBLE_CLICK_WINDOW = 0.35

HOLD_TIME = 3.0

BASE_GAIN = 35
MAX_GAIN = 120
SMOOTHING_ALPHA = 0.3
DEADZONE = 0.005

FONT = cv2.FONT_HERSHEY_SIMPLEX

# =========================
# MEDIAPIPE
# =========================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# =========================
# STATE
# =========================
smoothed_dir = np.array([0.0, 0.0])

vm = False
em = False

gesture_start = {"ONE": None, "TWO": None}

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
    results = hands.process(rgb)

    current_gesture = None

    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_lm, handedness in zip(
            results.multi_hand_landmarks,
            results.multi_handedness
        ):
            lm = hand_lm.landmark
            label = handedness.classification[0].label

            color = (0, 255, 0) if label == "Left" else (0, 0, 255)

            mp_draw.draw_landmarks(
                frame,
                hand_lm,
                mp_hands.HAND_CONNECTIONS,
                mp_draw.DrawingSpec(color=color, thickness=2, circle_radius=3),
                mp_draw.DrawingSpec(color=(200, 200, 200), thickness=2)
            )

            # Landmark indices
            for i, p in enumerate(lm):
                x, y = int(p.x * w), int(p.y * h)
                cv2.putText(frame, str(i), (x + 4, y - 4),
                            FONT, 0.35, (255, 255, 0), 1)

            # if label == "Left":
            #     p1 = (int(lm[5].x * w), int(lm[5].y * h))
            #     p2 = (int(lm[8].x * w), int(lm[8].y * h))
            #     cv2.arrowedLine(frame, p1, p2, (255, 255, 255), 2)
            #
            #     move_mouse_cartesian(lm)

            else:
                handle_pinch_clicks(lm)
                current_gesture = detect_right_gesture(lm)

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

cap.release()
cv2.destroyAllWindows()
