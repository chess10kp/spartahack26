import cv2
import mediapipe as mp
import pyautogui
import math
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

cap = cv2.VideoCapture(0)

pinch_active = False
PINCH_THRESHOLD = 0.03

VOICE_MODE_ACTIVE = False
THUMBS_UP_DEBOUNCE = 0.3
last_thumbs_up_time = 0

thumb_up_active = False


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def is_thumbs_up(landmarks):
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    thumb_mcp = landmarks[2]

    index_tip = landmarks[8]
    index_mcp = landmarks[5]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    thumb_up = thumb_tip.y < thumb_mcp.y

    index_curled = index_tip.y > index_mcp.y
    middle_curled = middle_tip.y > landmarks[9].y
    ring_curled = ring_tip.y > landmarks[13].y
    pinky_curled = pinky_tip.y > landmarks[17].y

    fingers_curled = index_curled and middle_curled and ring_curled and pinky_curled

    return thumb_up and fingers_curled


def get_voice_mode():
    return VOICE_MODE_ACTIVE


def process_frame(frame, trigger_voice_mode=None):
    global pinch_active, thumb_up_active, last_thumbs_up_time, VOICE_MODE_ACTIVE

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]

        is_pinch = distance(thumb_tip, index_tip) < PINCH_THRESHOLD

        if is_pinch and not pinch_active:
            pyautogui.click()
            pinch_active = True

        elif not is_pinch:
            pinch_active = False

        thumbs_up = is_thumbs_up(hand_landmarks.landmark)

        if thumbs_up:
            if not thumb_up_active:
                last_thumbs_up_time = time.time()
                thumb_up_active = True
        else:
            thumb_up_active = False

        if thumb_up_active and not VOICE_MODE_ACTIVE:
            elapsed = time.time() - last_thumbs_up_time
            if elapsed >= THUMBS_UP_DEBOUNCE:
                VOICE_MODE_ACTIVE = True
                if trigger_voice_mode:
                    trigger_voice_mode()

        if not thumbs_up and VOICE_MODE_ACTIVE:
            VOICE_MODE_ACTIVE = False

        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    return frame


def run_tracking(trigger_voice_mode=None):
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = process_frame(frame, trigger_voice_mode)

        cv2.imshow("Hand Tracking", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_tracking()
