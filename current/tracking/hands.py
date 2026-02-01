import cv2
import mediapipe as mp
import pyautogui
import math

# MediaPipe setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

cap = cv2.VideoCapture(1)

# Pinch state
pinch_active = False
PINCH_THRESHOLD = 0.03  # tweak if needed


def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


tracker = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

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
            print("CLICK", tracker)
            tracker += 1

        elif not is_pinch:
            pinch_active = False

        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

    cv2.imshow("Pinch Click", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
