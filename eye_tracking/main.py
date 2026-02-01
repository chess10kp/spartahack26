import cv2
import numpy as np
import time
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision
from evdev import UInput, ecodes as e

# ---------- Virtual Mouse Setup ----------
cap_events = {e.EV_REL: [e.REL_X, e.REL_Y], e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT]}
ui = UInput(cap_events, name="eye-tracker-mouse")


# ---------- Settings ----------
SCREEN_W, SCREEN_H = 2240, 1400
MODEL_PATH = "face_landmarker.task"
SENSITIVITY = 25.0
SMOOTH_FACTOR = 0.15
DEADZONE = 5

NOSE_BRIDGE = 4
IRIS_INDICES = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]

# ---------- Create Face Landmarker ----------
options = vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
)

landmarker = vision.FaceLandmarker.create_from_options(options)

# ---------- State ----------
curr_x, curr_y = SCREEN_W // 2, SCREEN_H // 2
calibrated_vector = None

cap = cv2.VideoCapture(0)
print("Press ESC to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = mp.Image(
        image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    )

    result = landmarker.detect_for_video(rgb_frame, int(time.time() * 1000))

    if result.face_landmarks:
        points = result.face_landmarks[0]
        nose = points[NOSE_BRIDGE]
        iris_x = np.mean([points[i].x for i in IRIS_INDICES])
        iris_y = np.mean([points[i].y for i in IRIS_INDICES])

        rel_vec = (iris_x - nose.x, iris_y - nose.y)
        if calibrated_vector is None:
            calibrated_vector = rel_vec

        target_x = int(
            SCREEN_W * (0.5 + (rel_vec[0] - calibrated_vector[0]) * SENSITIVITY)
        )
        target_y = int(
            SCREEN_H * (0.5 + (rel_vec[1] - calibrated_vector[1]) * SENSITIVITY)
        )

        new_x = curr_x + SMOOTH_FACTOR * (target_x - curr_x)
        new_y = curr_y + SMOOTH_FACTOR * (target_y - curr_y)

        dx = int(new_x - curr_x)
        dy = int(new_y - curr_y)

        if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
            ui.write(e.EV_REL, e.REL_X, dx)
            ui.write(e.EV_REL, e.REL_Y, dy)
            ui.syn()
            curr_x, curr_y = new_x, new_y

    cv2.imshow("Wayland Eye Tracker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

ui.close()
cap.release()
cv2.destroyAllWindows()
landmarker.close()
