import cv2
import torch
import numpy as np
import time
import json
import os
from pathlib import Path
from evdev import UInput, ecodes as e
from l2cs import Pipeline, render

# ---------- Virtual Mouse Setup ----------
cap_events = {e.EV_REL: [e.REL_X, e.REL_Y], e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT]}
ui = UInput(cap_events, name="l2cs-eye-tracker")

# ---------- Settings ----------
SCREEN_W, SCREEN_H = 2240, 1400
SMOOTH_FACTOR = 0.15
DEADZONE = 3
CALIBRATION_FILE = Path(__file__).parent / "calibration.json"

# ---------- Calibration Points (9-point grid) ----------
CALIB_POINTS = [
    (0.1, 0.1), (0.5, 0.1), (0.9, 0.1),
    (0.1, 0.5), (0.5, 0.5), (0.9, 0.5),
    (0.1, 0.9), (0.5, 0.9), (0.9, 0.9),
]


class GazeCalibration:
    def __init__(self):
        self.samples = []  # [(pitch, yaw, screen_x, screen_y), ...]
        self.coeffs_x = None
        self.coeffs_y = None
    
    def add_sample(self, pitch, yaw, screen_x, screen_y):
        self.samples.append((pitch, yaw, screen_x, screen_y))
    
    def fit(self):
        """Fit 2nd degree polynomial: screen = a*pitch^2 + b*yaw^2 + c*pitch*yaw + d*pitch + e*yaw + f"""
        if len(self.samples) < 6:
            return False
        
        data = np.array(self.samples)
        pitch, yaw = data[:, 0], data[:, 1]
        screen_x, screen_y = data[:, 2], data[:, 3]
        
        # Design matrix for 2nd degree polynomial
        X = np.column_stack([
            pitch**2, yaw**2, pitch*yaw, pitch, yaw, np.ones_like(pitch)
        ])
        
        # Least squares fit
        self.coeffs_x, _, _, _ = np.linalg.lstsq(X, screen_x, rcond=None)
        self.coeffs_y, _, _, _ = np.linalg.lstsq(X, screen_y, rcond=None)
        return True
    
    def predict(self, pitch, yaw):
        """Convert pitch/yaw to screen coordinates"""
        if self.coeffs_x is None:
            # Fallback: simple linear mapping before calibration
            x = SCREEN_W * (0.5 - yaw / 0.5)
            y = SCREEN_H * (0.5 + pitch / 0.5)
            return x, y
        
        features = np.array([pitch**2, yaw**2, pitch*yaw, pitch, yaw, 1.0])
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


def run_calibration(gaze_pipeline, cap, calibration):
    """Run 9-point calibration routine"""
    print("\n=== CALIBRATION MODE ===")
    print("Look at each dot and press SPACE when focused. Press ESC to skip.\n")
    
    for i, (px, py) in enumerate(CALIB_POINTS):
        screen_x = int(px * SCREEN_W)
        screen_y = int(py * SCREEN_H)
        
        # Create calibration display
        calib_frame = np.zeros((SCREEN_H, SCREEN_W, 3), dtype=np.uint8)
        cv2.circle(calib_frame, (screen_x, screen_y), 20, (0, 255, 0), -1)
        cv2.circle(calib_frame, (screen_x, screen_y), 5, (255, 255, 255), -1)
        cv2.putText(calib_frame, f"Point {i+1}/9 - Look here, press SPACE", 
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imshow("Calibration", calib_frame)
        
        # Collect samples for this point
        point_samples = []
        collecting = True
        
        while collecting:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame = cv2.flip(frame, 1)
            results = gaze_pipeline.step(frame)
            
            if results.pitch is not None and len(results.pitch) > 0:
                pitch = results.pitch[0].item()
                yaw = results.yaw[0].item()
                point_samples.append((pitch, yaw))
                
                # Show camera feed with gaze overlay
                frame = render(frame, results)
                cv2.imshow("Camera", frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                if len(point_samples) >= 10:
                    # Average the last 10 samples
                    avg_pitch = np.mean([s[0] for s in point_samples[-10:]])
                    avg_yaw = np.mean([s[1] for s in point_samples[-10:]])
                    calibration.add_sample(avg_pitch, avg_yaw, screen_x, screen_y)
                    print(f"Point {i+1} captured: pitch={avg_pitch:.3f}, yaw={avg_yaw:.3f}")
                    collecting = False
            elif key == 27:  # ESC
                cv2.destroyWindow("Calibration")
                return False
    
    cv2.destroyWindow("Calibration")
    
    if calibration.fit():
        calibration.save(CALIBRATION_FILE)
        print("\nCalibration complete and saved!")
        return True
    return False


def main():
    # Initialize L2CS-Net
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    gaze_pipeline = Pipeline(
        weights=Path(__file__).parent / 'models' / 'L2CSNet_gaze360.pkl',
        arch='ResNet50',
        device=device
    )
    
    cap = cv2.VideoCapture(0)
    calibration = GazeCalibration()
    
    # Try to load existing calibration
    if calibration.load(CALIBRATION_FILE):
        print("Loaded existing calibration.")
    else:
        print("No calibration found. Press 'c' to calibrate.")
    
    curr_x, curr_y = SCREEN_W // 2, SCREEN_H // 2
    prev_pitch, prev_yaw = None, None
    
    print("Press 'c' to calibrate, ESC to quit.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        results = gaze_pipeline.step(frame)
        
        if results.pitch is not None and len(results.pitch) > 0:
            pitch = results.pitch[0].item()
            yaw = results.yaw[0].item()
            
            # Smooth the gaze angles
            if prev_pitch is not None:
                pitch = prev_pitch + SMOOTH_FACTOR * (pitch - prev_pitch)
                yaw = prev_yaw + SMOOTH_FACTOR * (yaw - prev_yaw)
            prev_pitch, prev_yaw = pitch, yaw
            
            # Convert to screen coordinates
            target_x, target_y = calibration.predict(pitch, yaw)
            target_x = max(0, min(SCREEN_W - 1, target_x))
            target_y = max(0, min(SCREEN_H - 1, target_y))
            
            # Smooth cursor movement
            new_x = curr_x + SMOOTH_FACTOR * (target_x - curr_x)
            new_y = curr_y + SMOOTH_FACTOR * (target_y - curr_y)
            
            dx = int(new_x - curr_x)
            dy = int(new_y - curr_y)
            
            if abs(dx) > DEADZONE or abs(dy) > DEADZONE:
                ui.write(e.EV_REL, e.REL_X, dx)
                ui.write(e.EV_REL, e.REL_Y, dy)
                ui.syn()
                curr_x, curr_y = new_x, new_y
            
            # Render gaze visualization
            frame = render(frame, results)
        
        cv2.imshow("L2CS-Net Eye Tracker", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('c'):
            run_calibration(gaze_pipeline, cap, calibration)
    
    ui.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
