"""Minimal overlay displaying only hint labels on elements."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from gi import require_foreign, require_version
from pynput import keyboard

require_version("Gdk", "3.0")
require_version("Gtk", "3.0")
require_foreign("cairo")
from cairo import FONT_SLANT_NORMAL, FONT_WEIGHT_BOLD
from gi.repository import Gdk, Gtk

if TYPE_CHECKING:
    from cairo import Context

    from child import Child


class MinimalOverlayWindow(Gtk.Window):
    """Minimal overlay showing only hint labels on detected elements."""

    def __init__(
        self,
        config: dict[str, Any],
        hints: dict[str, Child],
        on_select: callable,
    ):
        """Minimal overlay constructor.

        :param config: Overlay configuration settings.
        :param hints: Dictionary of hint strings to Child objects.
        :param on_select: Callback function called when element is selected.
        """
        super().__init__(Gtk.WindowType.POPUP)

        self.hints = hints
        self.hint_selector_state = ""
        self.on_select = on_select
        self.hints_drawn_offsets: dict[str, tuple[float, float]] = {}

        # hint settings
        hints_config = config.get("hints", {})
        self.hint_height = hints_config.get("hint_height", 30)
        self.hint_width_padding = hints_config.get("hint_width_padding", 10)
        self.hint_font_size = hints_config.get("hint_font_size", 14)
        self.hint_font_face = hints_config.get("hint_font_face", "Sans")
        self.hint_font_r = hints_config.get("hint_font_r", 1.0)
        self.hint_font_g = hints_config.get("hint_font_g", 1.0)
        self.hint_font_b = hints_config.get("hint_font_b", 1.0)
        self.hint_font_a = hints_config.get("hint_font_a", 1.0)
        self.hint_background_r = hints_config.get("hint_background_r", 0.2)
        self.hint_background_g = hints_config.get("hint_background_g", 0.2)
        self.hint_background_b = hints_config.get("hint_background_b", 0.8)
        self.hint_background_a = hints_config.get("hint_background_a", 0.9)
        self.hint_upercase = hints_config.get("hint_upercase", True)

        self.exit_key = config.get("exit_key", "Escape")

        # composite setup
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        self.set_visual(visual)

        # window setup - transparent background
        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_accept_focus(True)
        self.set_sensitive(True)
        self.set_default_size(0, 0)

        # Setup window to cover entire screen
        display = Gdk.Display.get_default()
        screen = display.get_default_screen()
        monitor = display.get_monitor_at_point(0, 0)
        monitor_geometry = monitor.get_geometry()
        self.move(monitor_geometry.x, monitor_geometry.y)
        self.resize(monitor_geometry.width, monitor_geometry.height)

        self.drawing_area = Gtk.DrawingArea()
        self.connect("destroy", self.on_destroy)
        self.connect("key-press-event", self.on_key_press)
        self.connect("show", self.on_show)
        self.drawing_area.connect("draw", self.on_draw)

        vpaned = Gtk.VPaned()
        self.add(vpaned)
        vpaned.pack1(self.drawing_area, True, True)

    def on_draw(self, _, cr: Context):
        """Draw hint labels on elements.

        :param cr: Cairo Context.
        """
        hint_height = self.hint_height

        cr.select_font_face(self.hint_font_face, FONT_SLANT_NORMAL, FONT_WEIGHT_BOLD)
        cr.set_font_size(self.hint_font_size)

        for hint_value, child in self.hints.items():
            x_loc, y_loc = child.relative_position
            if x_loc >= 0 and y_loc >= 0:
                cr.save()
                utf8 = hint_value.upper() if self.hint_upercase else hint_value
                hint_state = (
                    self.hint_selector_state.upper()
                    if self.hint_upercase
                    else self.hint_selector_state
                )

                x_bearing, y_bearing, width, height, _, _ = cr.text_extents(utf8)
                hint_width = width + self.hint_width_padding

                cr.new_path()
                hint_x_offset = child.width / 2 - hint_width / 2
                hint_y_offset = child.height / 2 - hint_height / 2

                hint_x = x_loc + hint_x_offset
                hint_y = y_loc + hint_y_offset

                cr.translate(hint_x, hint_y)

                self.hints_drawn_offsets[hint_value] = (
                    hint_x_offset + hint_width / 2,
                    hint_y_offset + hint_height / 2,
                )

                cr.rectangle(0, 0, hint_width, hint_height)
                cr.set_source_rgba(
                    self.hint_background_r,
                    self.hint_background_g,
                    self.hint_background_b,
                    self.hint_background_a,
                )
                cr.fill()

                hint_text_position = (
                    (hint_width / 2) - (width / 2 + x_bearing),
                    (hint_height / 2) - (height / 2 + y_bearing),
                )

                cr.move_to(*hint_text_position)
                cr.set_source_rgba(
                    self.hint_font_r,
                    self.hint_font_g,
                    self.hint_font_b,
                    self.hint_font_a,
                )
                cr.show_text(utf8)

                cr.move_to(*hint_text_position)
                cr.set_source_rgba(0, 0, 0, 0.5)
                cr.show_text(hint_state)

                cr.close_path()
                cr.restore()

    def update_hints(self, next_char: str):
        """Update hints to eliminate non-matching options.

        :param next_char: Next character for hint_selector_state.
        """
        updated_hints = {
            hint: child
            for hint, child in self.hints.items()
            if hint.startswith(self.hint_selector_state + next_char)
        }

        if updated_hints:
            self.hints = updated_hints
            self.hint_selector_state += next_char

        self.drawing_area.queue_draw()

    def on_key_press(self, _, event):
        """Handle key presses for hint selection.

        :param event: Key press event.
        """
        keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())

        *_, consumed_modifiers = keymap.translate_keyboard_state(
            event.hardware_keycode,
            Gdk.ModifierType(event.state & ~Gdk.ModifierType.LOCK_MASK),
            1,
        )

        keyval_lower = Gdk.keyval_to_lower(event.keyval)

        if keyval_lower == Gdk.keyval_from_name(self.exit_key):
            self.destroy()

        hint_chr = chr(keyval_lower)

        self.update_hints(hint_chr)

        if len(self.hints) == 1:
            selected_hint = self.hint_selector_state
            child = self.hints[selected_hint]
            x, y = child.absolute_position
            x_offset, y_offset = self.hints_drawn_offsets[selected_hint]
            click_x = x + x_offset
            click_y = y + y_offset

            self.destroy()
            self.on_select(click_x, click_y)

    def on_show(self, window):
        """Setup window on show.

        Force keyboard grab to listen for keyboard events.

        :param window: Gtk Window object.
        """
        while (
            Gdk.keyboard_grab(window.get_window(), False, Gdk.CURRENT_TIME)
            != Gdk.GrabStatus.SUCCESS
        ):
            pass

        Gdk.Window.set_cursor(
            self.get_window(),
            Gdk.Cursor.new_from_name(Gdk.Display.get_default(), "none"),
        )

    def on_destroy(self, _):
        """Handle window destruction."""
        Gtk.main_quit()
