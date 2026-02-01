from pynput.mouse import Controller
import time

m = Controller()
for i in range(5):
    m.position = (100 + i * 50, 100)
    time.sleep(0.2)
    print("Moved to", m.position)
