"""Simple element selector using CLI instead of GTK overlay."""

import logging
from itertools import product
from math import ceil, log
import pygame

try:
    import pyscreenshot as ImageGrab
except ImportError:
    import PIL.ImageGrab
from cv2 import (
    CHAIN_APPROX_SIMPLE,
    COLOR_BGR2GRAY,
    RETR_LIST,
    Canny,
    boundingRect,
    cvtColor,
    dilate,
    findContours,
)
from numpy import array, ones, uint8

from child import Child
from mouse import click
from mouse_enums import MouseButton, MouseButtonState

logger = logging.getLogger(__name__)


def capture_screen():
    """Capture full screen screenshot."""
    try:
        return ImageGrab.grab(backend="grim")
    except Exception:
        return PIL.ImageGrab.grab()


def detect_elements(
    image,
    canny_min_val: int = 50,
    canny_max_val: int = 150,
    kernel_size: int = 3,
):
    """Detect UI elements using OpenCV edge detection."""
    children = []

    gray_image = cvtColor(array(image), COLOR_BGR2GRAY)

    edges = Canny(gray_image, canny_min_val, canny_max_val)

    kernel = ones((kernel_size, kernel_size), uint8)
    dilated_edges = dilate(edges, kernel)

    contours, _ = findContours(dilated_edges, RETR_LIST, CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = boundingRect(contour)

        if w > 20 and h > 20 and w < 800 and h < 600:
            children.append(
                Child(
                    absolute_position=(x, y),
                    relative_position=(x, y),
                    width=w,
                    height=h,
                )
            )

    logger.info(f"Detected {len(children)} elements")
    return children


def get_hints(children, alphabet: str = "asdfghjkl"):
    """Generate hint mapping from alphabet to detected elements."""
    hints = {}

    if len(children) == 0:
        return hints

    for child, hint in zip(
        children,
        product(alphabet, repeat=ceil(log(len(children)) / log(len(alphabet)))),
    ):
        hints["".join(hint)] = child

    return hints


def display_hints_via_pygame(screenshot, hints):
    """Display full-screen overlay with hints like GTK."""
    import os
    import time

    pygame.init()
    pygame.display.init()
    pygame.font.init()

    screen_width, screen_height = screenshot.size

    screen = pygame.display.set_mode(
        (screen_width, screen_height), pygame.FULLSCREEN | pygame.NOFRAME
    )
    pygame.display.set_caption("HintsOverlay")

    font = pygame.font.SysFont("Arial", 24, bold=True)
    clock = pygame.time.Clock()

    background = pygame.image.frombytes(screenshot.tobytes(), screenshot.size, "RGB")

    hint_state = ""
    result = None
    hints_drawn = {}
    last_key = ""

    running = True

    logger.info(f"Displaying {len(hints)} hints. Press ESC to quit.")

    time.sleep(0.2)

    while running:
        screen.blit(background, (0, 0))

        hint_bg_color = (0, 0, 0, 230)
        hint_text_color = (255, 255, 0)
        hint_height = 32
        hint_width_padding = 12

        for hint_value, child in hints.items():
            if hint_value.startswith(hint_state):
                x_loc, y_loc = child.absolute_position
                hint_text = hint_value.upper()
                text_surf = font.render(hint_text, True, hint_text_color)
                text_rect = text_surf.get_rect()

                hint_width = text_rect.width + hint_width_padding * 2
                hint_x_offset = child.width / 2 - hint_width / 2
                hint_y_offset = child.height / 2 - hint_height / 2

                hint_x = int(x_loc + hint_x_offset)
                hint_y = int(y_loc + hint_y_offset)

                hint_surface = pygame.Surface(
                    (hint_width, hint_height), pygame.SRCALPHA
                )
                hint_surface.fill(hint_bg_color)

                text_x = (hint_width - text_rect.width) // 2
                text_y = (hint_height - text_rect.height) // 2
                hint_surface.blit(text_surf, (text_x, text_y))

                screen.blit(hint_surface, (hint_x, hint_y))
                hints_drawn[hint_value] = (hint_x, hint_y)

        status_text = f"Typed: {last_key.upper()} | ESC to quit | Hints: {sum(1 for h in hints.keys() if h.startswith(hint_state))}"
        status_surf = font.render(status_text, True, (255, 255, 255))

        bg_status = pygame.Surface(
            (status_surf.get_width() + 20, status_surf.get_height() + 10),
            pygame.SRCALPHA,
        )
        bg_status.fill((0, 0, 0, 200))
        screen.blit(bg_status, (20, 20))
        screen.blit(status_surf, (30, 25))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                result = "q"
                running = False
            elif event.type == pygame.KEYDOWN:
                logger.info(f"Key pressed: {event.key} ({event.unicode})")
                last_key = event.unicode

                if event.key == pygame.K_ESCAPE:
                    result = "q"
                    running = False
                elif event.unicode.isalpha():
                    next_char = event.unicode.lower()
                    hint_state += next_char

                    updated_hints = {
                        h: c for h, c in hints.items() if h.startswith(hint_state)
                    }

                    logger.info(
                        f"Hint state: {hint_state}, Remaining hints: {len(updated_hints)}"
                    )

                    if len(updated_hints) == 1:
                        result = list(updated_hints.keys())[0]
                        running = False
                    elif len(updated_hints) == 0:
                        hint_state = hint_state[:-1]

        clock.tick(30)

    pygame.quit()
    logger.info(f"Result: {result}")
    return result.lower() if result else "q"


def run_element_selection_cli():
    """Run element selection using pygame window for input."""
    logger.info("Starting element selection mode")

    try:
        screenshot = capture_screen()
        children = detect_elements(screenshot)
        hints = get_hints(children)

        print(f"\nDetected {len(hints)} elements:")

        user_input = display_hints_via_pygame(screenshot, hints)

        if user_input == "q":
            print("Quitting...")
        elif user_input in hints:
            child = hints[user_input]
            x, y = child.absolute_position
            center_x = int(x + child.width / 2)
            center_y = int(y + child.height / 2)

            logger.info(f"Clicking at ({center_x}, {center_y})")
            click(
                center_x,
                center_y,
                MouseButton.LEFT,
                (MouseButtonState.DOWN, MouseButtonState.UP),
                1,
            )
            print(f"Clicked at ({center_x}, {center_y})")
        else:
            print(f"Invalid hint.")

    except Exception as e:
        logger.error(f"Element selection failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    run_element_selection_cli()
