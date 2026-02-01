import PIL.ImageGrab
import datetime
import os


def main():
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join("screenshots", f"screenshot_{timestamp}.png")
    screenshot = PIL.ImageGrab.grab()
    screenshot.save(filename)
    print(f"Screenshot saved as {filename}")


if __name__ == "__main__":
    main()
