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


screen_w, screen_h = pyautogui.size()

print(f"OS: {platform.system()}")
print(f"Screen size: {screen_w}x{screen_h}")

print("Moving to center...")
move_mouse(screen_w // 2, screen_h // 2)
time.sleep(2)

print("Moving up...")
move_mouse(screen_w // 2, 0)
time.sleep(2)

print("Done!")
