import time
import pyautogui

screen_w, screen_h = pyautogui.size()

print("Moving to center...")
pyautogui.moveTo(screen_w // 2, screen_h // 2)
print(f"Center: ({screen_w // 2}, {screen_h // 2})")
time.sleep(5)

print("Moving up...")
pyautogui.moveTo(screen_w // 2, 0)
print(f"Up: ({screen_w // 2}, 0)")
time.sleep(5)

print("Done!")
