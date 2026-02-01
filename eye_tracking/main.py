import cv2
import numpy as np
import platform
import subprocess
import random
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

# ---------- OS Detection & Mouse Control ----------
use_ydotool = (
    platform.system() == "Linux"
    and subprocess.run(["which", "ydotool"], capture_output=True).returncode == 0
)
use_pynput = platform.system() == "Linux" and not use_ydotool

if use_ydotool:
    print("Using ydotool for mouse control")
    SCREEN_W, SCREEN_H = 2240, 1400  # Default, will be detected
elif use_pynput:
    print("Using pynput for mouse control")
    from pynput.mouse import Controller

    mouse = Controller()
    SCREEN_W = mouse._display.screen().width_in_pixels
    SCREEN_H = mouse._display.screen().height_in_pixels
else:
    print("Using pyautogui for mouse control")
    import pyautogui

    mouse = pyautogui
    SCREEN_W, SCREEN_H = pyautogui.size()
    pyautogui.FAILSAFE = False


def move_mouse(x, y):
    if use_ydotool:
        subprocess.run(
            ["ydotool", "mousemove", "-a", str(x), str(y)], capture_output=True
        )
    elif use_pynput:
        mouse.position = (x, y)
    else:
        pyautogui.moveTo(x, y)


# ---------- Settings ----------
MODEL_PATH = "face_landmarker.task"  # downloaded file
SMOOTHING = 0.25  # 0.10–0.25
SCALE_X = 10.0  # sensitivity
SCALE_Y = 10.0
DEADZONE = 1  # pixels to ignore jitter

# Iris landmark indices in FaceLandmarker output (same numbering as FaceMesh)
RIGHT_IRIS = [469, 470, 471, 472]

# ---------- Create Face Landmarker ----------
options = vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=False,
)

landmarker = vision.FaceLandmarker.create_from_options(options)

# ---------- State ----------
prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
prev_ix, prev_iy = 0.5, 0.5
calibrated = False
base_ix, base_iy = 0.5, 0.5
calib_samples = []

cap = cv2.VideoCapture(0)
print(
    "Look at the CENTER of your screen for ~2 seconds to auto-calibrate. Press ESC to quit."
)

frame_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # MediaPipe expects RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    # timestamp in ms required for VIDEO mode
    timestamp_ms = int(frame_id * (1000 / max(cap.get(cv2.CAP_PROP_FPS), 30)))
    result = landmarker.detect_for_video(mp_image, timestamp_ms)

    if result.face_landmarks:
        landmarks = result.face_landmarks[0]

        # average iris center (normalized [0,1])
        ix = iy = 0.0
        for idx in RIGHT_IRIS:
            lm = landmarks[idx]
            ix += lm.x
            iy += lm.y
        ix /= len(RIGHT_IRIS)
        iy /= len(RIGHT_IRIS)

        # calibration for first ~60 frames
        if not calibrated:
            calib_samples.append((ix, iy))
            if len(calib_samples) >= 60:
                base_ix = float(np.mean([s[0] for s in calib_samples]))
                base_iy = float(np.mean([s[1] for s in calib_samples]))
                calibrated = True
                print(f"Calibrated center: ({base_ix:.3f}, {base_iy:.3f})")

        # delta from center
        dx = (ix - base_ix) * SCALE_X
        dy = (iy - base_iy) * SCALE_Y

        # map to screen
        target_x = int(SCREEN_W * (0.5 + dx))
        target_y = int(SCREEN_H * (0.5 + dy))

        # clamp
        target_x = max(0, min(SCREEN_W - 1, target_x))
        target_y = max(0, min(SCREEN_H - 1, target_y))

        # only move if iris position has changed significantly (0.005 threshold)
        iris_delta = abs(ix - prev_ix) + abs(iy - prev_iy)
        if iris_delta > 0.005:
            print(
                f"Iris moved by {iris_delta:.4f}, moving mouse to ({target_x}, {target_y})"
            )
            move_mouse(target_x, target_y)
            prev_ix, prev_iy = ix, iy
    else:
        cv2.putText(
            frame,
            "No face detected",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2,
        )

    cv2.imshow("Eye Cursor (MediaPipe Tasks)", frame)
    frame_id += 1

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
landmarker.close()
