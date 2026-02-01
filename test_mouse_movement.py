import time
import platform
import subprocess
import pyautogui


def move_mouse(x, y):
    system = platform.system()

    if system == "Linux":
        if subprocess.run(["which", "ydotool"], capture_output=True).returncode == 0:
            subprocess.run(
                ["ydotool", "mousemove", str(x), str(y)], capture_output=True
            )
            print(f"Moved to ({x}, {y}) using ydotool")
            return
        try:
            from pynput.mouse import Controller

            mouse = Controller()
            mouse.position = (x, y)
            print(f"Moved to ({x}, {y}) using pynput")
            return
        except ImportError:
            pass

    pyautogui.moveTo(x, y)
    print(f"Moved to ({x}, {y}) using pyautogui")


print(f"OS: {platform.system()}")
print("Testing mouse movement...")
print("Screen size:", pyautogui.size())

screen_w, screen_h = pyautogui.size()

# Test 1: Move to corners
move_mouse(0, 0)
time.sleep(0.5)
move_mouse(screen_w, 0)
time.sleep(0.5)
move_mouse(screen_w, screen_h)
time.sleep(0.5)
move_mouse(0, screen_h)
time.sleep(0.5)

# Test 2: Move to center
move_mouse(screen_w // 2, screen_h // 2)
time.sleep(0.5)

# Test 3: Circle pattern
cx, cy = screen_w // 2, screen_h // 2
radius = 200
import math

for i in range(360):
    angle = math.radians(i)
    x = int(cx + radius * math.cos(angle))
    y = int(cy + radius * math.sin(angle))
    move_mouse(x, y)
    time.sleep(0.01)

print("Done!")
