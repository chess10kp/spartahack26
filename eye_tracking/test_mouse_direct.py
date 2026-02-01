from pynput.mouse import Controller
import time

m = Controller()
print(f"Initial position: {m.position}")

# Test 1: Set to (100, 100)
m.position = (100, 100)
time.sleep(0.1)
print(f"After setting to (100, 100): {m.position}")

# Test 2: Set to (500, 500)
m.position = (500, 500)
time.sleep(0.1)
print(f"After setting to (500, 500): {m.position}")

# Test 3: Try with large movement
m.position = (1000, 700)
time.sleep(0.1)
print(f"After setting to (1000, 700): {m.position}")
