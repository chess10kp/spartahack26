import cv2
import numpy as np
from pynput.mouse import Controller
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

# ---------- Settings ----------
MODEL_PATH = "face_landmarker.task"  # downloaded file
SMOOTHING = 0.25  # 0.10–0.25
SCALE_X = 1.35  # sensitivity
SCALE_Y = 1.35
DEADZONE = 5  # pixels to ignore jitter
mouse = Controller()
SCREEN_W = mouse._display.screen().width_in_pixels
SCREEN_H = mouse._display.screen().height_in_pixels

# Iris landmark indices in FaceLandmarker output (same numbering as FaceMesh)
RIGHT_IRIS = [469, 470, 471, 472]

# ---------- Create Face Landmarker ----------
options = vision.FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1,
    output_face_blendshapes=False,
    output_facial_transformation_matrixes=False,
)

landmarker = vision.FaceLandmarker.create_from_options(options)

# ---------- State ----------
prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
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
        target_x = int(SCREEN_W / 2 + dx * SCREEN_W)
        target_y = int(SCREEN_H / 2 + dy * SCREEN_H)

        # clamp
        target_x = max(0, min(SCREEN_W - 1, target_x))
        target_y = max(0, min(SCREEN_H - 1, target_y))

        # smoothing
        curr_x = int(prev_x + (target_x - prev_x) * SMOOTHING)
        curr_y = int(prev_y + (target_y - prev_y) * SMOOTHING)

        # deadzone (ignore tiny jitter)
        if abs(curr_x - prev_x) + abs(curr_y - prev_y) > DEADZONE:
            print(f"Moving to ({curr_x}, {curr_y})")
            mouse.position = (curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

        # debug dot on camera view
        cv2.circle(frame, (int(ix * w), int(iy * h)), 5, (0, 255, 0), -1)
        cv2.putText(
            frame,
            "Tracking" if calibrated else "Calibrating...",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0) if calibrated else (0, 255, 255),
            2,
        )
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
