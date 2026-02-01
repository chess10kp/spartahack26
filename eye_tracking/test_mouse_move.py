from pynput.mouse import Controller
import time

m = Controller()
print(f"Initial position: {m.position}")

# Test 1: Use move() for relative movement
m.move(-1020, -600)  # Move from (1120, 700) to (100, 100)
time.sleep(0.1)
print(f"After moving to (100, 100) using move(): {m.position}")

# Test 2: Use position for absolute movement
m.position = (500, 500)
time.sleep(0.1)
print(f"After setting to (500, 100) using position: {m.position}")

# Test 3: Use move() again
m.move(500, 200)  # Move from (500, 500) to (1000, 700)
time.sleep(0.1)
print(f"After moving to (1000, 700) using move(): {m.position}")
