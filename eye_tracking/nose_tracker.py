import cv2
import numpy as np
import time
import json
import os
from pathlib import Path
from evdev import UInput, ecodes as e
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

# ---------- Virtual Mouse Setup ----------
# NOTE: UInput is now created lazily in NoseTracker.start() to avoid module-level side effects
CAP_EVENTS = {e.EV_REL: [e.REL_X, e.REL_Y], e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT]}

# ---------- Settings ----------
SCREEN_W, SCREEN_H = 2240, 1400
MODEL_PATH = Path(__file__).parent / "face_landmarker.task"
SMOOTH_FACTOR = 0.4  # Higher = more responsive
DEADZONE = 1  # Lower = catches smaller movements
SENSITIVITY = 10  # Multiplier for movement
CALIBRATION_FILE = Path(__file__).parent / "nose_calibration.json"

NOSE_TIP = 1  # Nose tip landmark index

# ---------- Blink Detection Settings ----------
# Eye landmark indices (MediaPipe face mesh)
# Left eye: upper lid [159, 145], lower lid [145, 153], corners [33, 133]
# Right eye: upper lid [386, 374], lower lid [374, 380], corners [362, 263]
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]  # corners and vertical points
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
EAR_THRESHOLD = 0.2  # Below this = blink
BLINK_CONSEC_FRAMES = 2  # Frames eye must be closed to count as blink
DOUBLE_BLINK_WINDOW = 0.6  # Seconds between blinks for double-blink

# ---------- Calibration Points (9-point grid) ----------
CALIB_POINTS = [
    (0.1, 0.1),
    (0.5, 0.1),
    (0.9, 0.1),
    (0.1, 0.5),
    (0.5, 0.5),
    (0.9, 0.5),
    (0.1, 0.9),
    (0.5, 0.9),
    (0.9, 0.9),
]


def eye_aspect_ratio(landmarks, eye_indices):
    """Calculate Eye Aspect Ratio (EAR) for blink detection.

    EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)
    Where p1,p4 are corners, p2,p6 and p3,p5 are vertical points.
    """

    def dist(p1, p2):
        return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

    p1 = landmarks[eye_indices[0]]  # left corner
    p2 = landmarks[eye_indices[1]]  # upper1
    p3 = landmarks[eye_indices[2]]  # upper2
    p4 = landmarks[eye_indices[3]]  # right corner
    p5 = landmarks[eye_indices[4]]  # lower2
    p6 = landmarks[eye_indices[5]]  # lower1

    vertical1 = dist(p2, p6)
    vertical2 = dist(p3, p5)
    horizontal = dist(p1, p4)

    if horizontal == 0:
        return 0.3  # Default open value

    ear = (vertical1 + vertical2) / (2.0 * horizontal)
    return ear


class NoseCalibration:
    def __init__(self):
        self.samples = []  # [(nose_x, nose_y, screen_x, screen_y), ...]
        self.coeffs_x = None
        self.coeffs_y = None

    def add_sample(self, nose_x, nose_y, screen_x, screen_y):
        self.samples.append((nose_x, nose_y, screen_x, screen_y))

    def fit(self):
        """Fit 2nd degree polynomial"""
        if len(self.samples) < 6:
            return False

        data = np.array(self.samples)
        nose_x, nose_y = data[:, 0], data[:, 1]
        screen_x, screen_y = data[:, 2], data[:, 3]

        X = np.column_stack(
            [
                nose_x**2,
                nose_y**2,
                nose_x * nose_y,
                nose_x,
                nose_y,
                np.ones_like(nose_x),
            ]
        )

        self.coeffs_x, _, _, _ = np.linalg.lstsq(X, screen_x, rcond=None)
        self.coeffs_y, _, _, _ = np.linalg.lstsq(X, screen_y, rcond=None)
        return True

    def predict(self, nose_x, nose_y):
        """Convert nose position to screen coordinates"""
        if self.coeffs_x is None:
            # Fallback: simple linear mapping
            x = SCREEN_W * nose_x
            y = SCREEN_H * nose_y
            return x, y

        features = np.array(
            [nose_x**2, nose_y**2, nose_x * nose_y, nose_x, nose_y, 1.0]
        )
        x = np.dot(features, self.coeffs_x)
        y = np.dot(features, self.coeffs_y)
        return float(x), float(y)

    def save(self, path):
        data = {
            "samples": self.samples,
            "coeffs_x": self.coeffs_x.tolist() if self.coeffs_x is not None else None,
            "coeffs_y": self.coeffs_y.tolist() if self.coeffs_y is not None else None,
        }
        with open(path, "w") as f:
            json.dump(data, f)

    def load(self, path):
        if not os.path.exists(path):
            return False
        with open(path) as f:
            data = json.load(f)
        self.samples = data["samples"]
        self.coeffs_x = np.array(data["coeffs_x"]) if data["coeffs_x"] else None
        self.coeffs_y = np.array(data["coeffs_y"]) if data["coeffs_y"] else None
        return self.coeffs_x is not None


def run_calibration(landmarker, cap, calibration):
    """Run 9-point calibration routine"""
    print("\n=== CALIBRATION MODE ===")
    print("Point your nose at each dot and press SPACE. Press ESC to skip.\n")

    for i, (px, py) in enumerate(CALIB_POINTS):
        screen_x = int(px * SCREEN_W)
        screen_y = int(py * SCREEN_H)

        point_samples = []
        collecting = True
        frame_id = 0

        while collecting:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            timestamp_ms = int(frame_id * (1000 / 30))
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            frame_id += 1

            if result.face_landmarks:
                nose = result.face_landmarks[0][NOSE_TIP]
                point_samples.append((nose.x, nose.y))

                # Draw nose position on camera feed
                h, w, _ = frame.shape
                cv2.circle(
                    frame, (int(nose.x * w), int(nose.y * h)), 10, (0, 255, 0), -1
                )

            # Draw calibration overlay on frame
            h, w = frame.shape[:2]
            cv2.rectangle(frame, (10, 10), (600, 80), (0, 0, 0), -1)
            cv2.putText(
                frame,
                f"Point {i + 1}/9 - Point nose here, press SPACE",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                if len(point_samples) >= 10:
                    avg_x = np.mean([s[0] for s in point_samples[-10:]])
                    avg_y = np.mean([s[1] for s in point_samples[-10:]])
                    calibration.add_sample(avg_x, avg_y, screen_x, screen_y)
                    print(f"Point {i + 1} captured: nose=({avg_x:.3f}, {avg_y:.3f})")
                    collecting = False
            elif key == 27:  # ESC
                return False

    if calibration.fit():
        calibration.save(CALIBRATION_FILE)
        print("\nCalibration complete and saved!")
        return True
    return False


def main():
    options = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
    )
    landmarker = vision.FaceLandmarker.create_from_options(options)

    # Create UInput here for standalone mode
    ui = UInput(CAP_EVENTS, name="nose-tracker-mouse")

    cap = cv2.VideoCapture(0)
    calibration = NoseCalibration()

    if calibration.load(CALIBRATION_FILE):
        print("Loaded existing calibration.")
    else:
        print("No calibration found. Press 'c' to calibrate.")

    curr_x, curr_y = SCREEN_W // 2, SCREEN_H // 2
    prev_nose_x, prev_nose_y = None, None
    frame_id = 0

    print("Press 'c' to calibrate, ESC to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int(frame_id * (1000 / 30))
        result = landmarker.detect_for_video(mp_image, timestamp_ms)
        frame_id += 1

        if result.face_landmarks:
            nose = result.face_landmarks[0][NOSE_TIP]
            nose_x, nose_y = nose.x, nose.y

            # Smooth nose position
            if prev_nose_x is not None:
                nose_x = prev_nose_x + SMOOTH_FACTOR * (nose_x - prev_nose_x)
                nose_y = prev_nose_y + SMOOTH_FACTOR * (nose_y - prev_nose_y)
            prev_nose_x, prev_nose_y = nose_x, nose_y

            # Convert to screen coordinates with sensitivity boost
            target_x, target_y = calibration.predict(nose_x, nose_y)
            # Apply sensitivity around screen center
            target_x = SCREEN_W / 2 + (target_x - SCREEN_W / 2) * SENSITIVITY
            target_y = SCREEN_H / 2 + (target_y - SCREEN_H / 2) * SENSITIVITY
            target_x = max(0, min(SCREEN_W - 1, target_x))
            target_y = max(0, min(SCREEN_H - 1, target_y))

            # Smooth cursor movement
            new_x = curr_x + SMOOTH_FACTOR * (target_x - curr_x)
            new_y = curr_y + SMOOTH_FACTOR * (target_y - curr_y)

            dx = int(new_x - curr_x)
            dy = int(new_y - curr_y)

            if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
                ui.write(e.EV_REL, e.REL_X, -dx)
                ui.write(e.EV_REL, e.REL_Y, dy)
                ui.syn()
                curr_x, curr_y = new_x, new_y

            # Draw nose on frame
            h, w, _ = frame.shape
            cv2.circle(frame, (int(nose.x * w), int(nose.y * h)), 10, (0, 255, 0), -1)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord("c"):
            run_calibration(landmarker, cap, calibration)
            frame_id = 0

    ui.close()
    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


class NoseTracker:
    """Reusable nose tracker that can be started/stopped"""

    def __init__(self):
        self.landmarker = None
        self.calibration = NoseCalibration()
        self.curr_x, self.curr_y = SCREEN_W // 2, SCREEN_H // 2
        self.prev_nose_x, self.prev_nose_y = None, None
        self.frame_id = 0
        self.ui = None
        self.active = False

        # Blink detection state
        self.blink_counter = 0  # Consecutive frames with closed eyes
        self.blink_times = []  # Timestamps of detected blinks
        self.eyes_were_closed = False

    def start(self):
        if self.active:
            return

        options = vision.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

        self.ui = UInput(CAP_EVENTS, name="nose-tracker-mouse")

        self.calibration.load(CALIBRATION_FILE)
        self.frame_id = 0
        self.prev_nose_x, self.prev_nose_y = None, None
        self.blink_counter = 0
        self.blink_times = []
        self.eyes_were_closed = False
        self.active = True
        print("Nose tracker started")

    def stop(self):
        if not self.active:
            return

        if self.landmarker:
            self.landmarker.close()
            self.landmarker = None
        if self.ui:
            self.ui.close()
            self.ui = None
        self.active = False
        print("Nose tracker stopped")

    def detect_blinks(self, landmarks):
        """Detect blinks from face landmarks.

        Returns:
            blink_count: 0=no blink, 1=single blink, 2=double blink
        """
        now = time.time()

        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE_IDX)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE_IDX)
        avg_ear = (left_ear + right_ear) / 2.0

        eyes_closed = avg_ear < EAR_THRESHOLD

        if eyes_closed:
            self.blink_counter += 1
        else:
            if self.blink_counter >= BLINK_CONSEC_FRAMES:
                self.blink_times.append(now)
                self.blink_times = [
                    t for t in self.blink_times if now - t < DOUBLE_BLINK_WINDOW
                ]

                if len(self.blink_times) >= 2:
                    self.blink_times = []
                    self.blink_counter = 0
                    return 2

                if len(self.blink_times) == 1:
                    self.blink_times = []
                    self.blink_counter = 0
                    return 1

            self.blink_counter = 0

        return 0

    def process_frame(self, frame):
        """Process a frame and move mouse. Returns (frame, blink_count)."""
        if not self.active or self.landmarker is None:
            return frame, 0

        blink_count = 0
        # NOTE: Do NOT flip frame here - caller already flips it
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        timestamp_ms = int(self.frame_id * (1000 / 30))
        result = self.landmarker.detect_for_video(mp_image, timestamp_ms)
        self.frame_id += 1

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]
            nose = landmarks[NOSE_TIP]
            nose_x, nose_y = nose.x, nose.y

            blink_count = self.detect_blinks(landmarks)

            # Smooth nose position
            if self.prev_nose_x is not None:
                nose_x = self.prev_nose_x + SMOOTH_FACTOR * (nose_x - self.prev_nose_x)
                nose_y = self.prev_nose_y + SMOOTH_FACTOR * (nose_y - self.prev_nose_y)
            self.prev_nose_x, self.prev_nose_y = nose_x, nose_y

            # Convert to screen coordinates with sensitivity
            target_x, target_y = self.calibration.predict(nose_x, nose_y)
            target_x = SCREEN_W / 2 + (target_x - SCREEN_W / 2) * SENSITIVITY
            target_y = SCREEN_H / 2 + (target_y - SCREEN_H / 2) * SENSITIVITY
            target_x = max(0, min(SCREEN_W - 1, target_x))
            target_y = max(0, min(SCREEN_H - 1, target_y))

            # Smooth cursor movement
            new_x = self.curr_x + SMOOTH_FACTOR * (target_x - self.curr_x)
            new_y = self.curr_y + SMOOTH_FACTOR * (target_y - self.curr_y)

            dx = int(new_x - self.curr_x)
            dy = int(new_y - self.curr_y)

            if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
                self.ui.write(e.EV_REL, e.REL_X, -dx)
                self.ui.write(e.EV_REL, e.REL_Y, dy)
                self.ui.syn()
                self.curr_x, self.curr_y = new_x, new_y

            # Draw nose on frame
            h, w, _ = frame.shape
            cv2.circle(frame, (int(nose.x * w), int(nose.y * h)), 10, (0, 255, 0), -1)

            # Draw blink indicator
            if self.blink_counter > 0:
                cv2.putText(
                    frame,
                    "BLINK",
                    (w - 100, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2,
                )

        return frame, blink_count


if __name__ == "__main__":
    main()
