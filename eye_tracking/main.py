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
SENSITIVITY_X = 20.0
SENSITIVITY_Y = 40.0
SMOOTH_FACTOR = 0.15
DEADZONE = 5

NOSE_BRIDGE = 4
LEFT_EYE_CORNER = 33
RIGHT_EYE_CORNER = 263
IRIS_INDICES = [468, 469, 470, 471, 472, 473, 474, 475, 476, 477]

# ---------- Create Face Landmarker ----------
options = vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    output_face_blendshapes=True,
)

landmarker = vision.FaceLandmarker.create_from_options(options)

# ---------- State ----------
curr_x, curr_y = SCREEN_W // 2, SCREEN_H // 2
calibrated_vector = None
prev_nose = None
prev_rel_vec = None
HEAD_MOVE_THRESHOLD = 0.01  # Ignore eye movement when head moves this much
BLINK_THRESHOLD = 0.5  # Blendshape score above this = blink detected

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

    if result.face_landmarks and result.face_blendshapes:
        # Check for blinks
        blendshapes = {b.category_name: b.score for b in result.face_blendshapes[0]}
        if blendshapes.get("eyeBlinkLeft", 0) > BLINK_THRESHOLD or blendshapes.get("eyeBlinkRight", 0) > BLINK_THRESHOLD:
            continue  # Skip this frame during blink
        
        points = result.face_landmarks[0]
        nose = points[NOSE_BRIDGE]
        left_corner = points[LEFT_EYE_CORNER]
        right_corner = points[RIGHT_EYE_CORNER]
        
        # Use eye width to normalize for distance/scale changes
        eye_width = np.sqrt((right_corner.x - left_corner.x)**2 + (right_corner.y - left_corner.y)**2)
        eye_center_x = (left_corner.x + right_corner.x) / 2
        eye_center_y = (left_corner.y + right_corner.y) / 2
        
        iris_x = np.mean([points[i].x for i in IRIS_INDICES])
        iris_y = np.mean([points[i].y for i in IRIS_INDICES])

        # Normalize iris position relative to eye frame (scale-invariant)
        rel_vec = ((iris_x - eye_center_x) / eye_width, (iris_y - eye_center_y) / eye_width)
        
        if calibrated_vector is None:
            calibrated_vector = rel_vec
            prev_nose = (nose.x, nose.y)
            prev_rel_vec = rel_vec
            continue

        # Detect head movement
        head_delta = np.sqrt((nose.x - prev_nose[0])**2 + (nose.y - prev_nose[1])**2)
        prev_nose = (nose.x, nose.y)
        
        # If head moved significantly, update calibration to compensate
        if head_delta > HEAD_MOVE_THRESHOLD:
            # Adjust calibration vector to cancel out head-induced eye shift
            calibrated_vector = (
                calibrated_vector[0] + (rel_vec[0] - prev_rel_vec[0]),
                calibrated_vector[1] + (rel_vec[1] - prev_rel_vec[1])
            )
        
        prev_rel_vec = rel_vec

        target_x = int(
            SCREEN_W * (0.5 + (rel_vec[0] - calibrated_vector[0]) * SENSITIVITY_X)
        )
        target_y = int(
            SCREEN_H * (0.5 + (rel_vec[1] - calibrated_vector[1]) * SENSITIVITY_Y)
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
