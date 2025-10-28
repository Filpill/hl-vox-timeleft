"""
UIManager class for Half-Life VOX TimeLEFT application.
Handles all GUI creation, updates, and event callbacks.
"""

import os
import dearpygui.dearpygui as dpg
from typing import Callable, Optional

from libs.config import Config
from libs.asset_manager import AssetManager
from libs.timer import Timer
from libs.audio_manager import AudioManager


class UIManager:
    """Manages all GUI operations and event callbacks."""

    def __init__(
        self,
        asset_manager: AssetManager,
        audio_manager: AudioManager,
        timer: Timer
    ):
        """
        Initialize the UI manager.

        Args:
            asset_manager: AssetManager instance
            audio_manager: AudioManager instance
            timer: Timer instance
        """
        self.asset_manager = asset_manager
        self.audio_manager = audio_manager
        self.timer = timer

        # UI state
        self.bg_texture_path = None
        self.large_font = None

    def initialize_gui(self):
        """Initialize DearPyGUI context and create all GUI elements."""
        dpg.create_context()

        # Load initial background texture
        self.bg_texture_path = self.asset_manager.get_background_texture_path()
        width, height, channels, data = dpg.load_image(self.bg_texture_path)

        # Register assets
        self._register_fonts()
        self._register_textures(width, height, data)
        self._create_drawlist()
        self._create_main_window()
        self._setup_viewport()
        self._configure_callbacks()
        self._finalize_setup()

    def _register_fonts(self):
        """Register font assets."""
        font_path = self.asset_manager.get_font_path("trebuc.ttf")
        with dpg.font_registry():
            self.large_font = dpg.add_font(font_path, 48)

    def _register_textures(self, width: int, height: int, data):
        """Register texture assets."""
        with dpg.texture_registry():
            dpg.add_dynamic_texture(width, height, data, tag=Config.IMAGE_TAG)

    def _create_drawlist(self):
        """Create viewport drawlist for background image."""
        with dpg.viewport_drawlist(front=True, tag=Config.DRAWLIST_TAG):
            dpg.draw_image(
                Config.IMAGE_TAG,
                pmin=(0, 0),
                pmax=(Config.IMAGE_WIDTH, Config.IMAGE_HEIGHT)
            )

            bg_name = self.bg_texture_path.rsplit('/', 1)[-1]
            dpg.draw_text(
                text=bg_name,
                pos=(2, Config.IMAGE_HEIGHT - 15),
                size=14,
                color=(255, 255, 255, 255)
            )

    def _create_main_window(self):
        """Create main window with all UI elements."""
        with dpg.window(tag="Timer Window"):
            # Spacer for background image
            dpg.add_spacer(height=Config.IMAGE_HEIGHT - 5)

            # Change background button
            dpg.add_button(
                label="Change Background",
                tag=Config.BACKGROUND_TAG,
                callback=self._callback_change_bg
            )

            # Weapon selection group
            with dpg.group(horizontal=True):
                with dpg.group(horizontal=False):
                    dpg.add_text("Select Gun")
                    dpg.add_combo(
                        tag=Config.GUN_TAG,
                        default_value="glock18",
                        items=self.asset_manager.load_gun_names(),
                        callback=self._callback_weapon_select,
                        width=100
                    )
                dpg.add_button(
                    label="Fire",
                    tag=Config.SHOOT_TAG,
                    callback=self._callback_shootgun,
                    height=45,
                    width=127
                )

            # Timer display
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=30)
                dpg.add_text("00:00:00", tag=Config.TIMER_TAG)

            dpg.add_spacer(height=10)

            # Time input field
            dpg.add_input_text(
                label="HH:MM:SS",
                hint="HH:MM:SS",
                default_value=Config.DEFAULT_POMODORO_TIME,
                tag=Config.INPUT_TAG
            )

            # Control buttons
            with dpg.group(horizontal=True):
                dpg.add_button(label="Start Timer", tag=Config.START_TAG)
                dpg.add_button(label="Pause", tag=Config.PAUSE_TAG)
                dpg.add_button(label="Reset Timer", tag=Config.RESET_TAG)

            # Time-left button
            dpg.add_button(label="Timeleft", tag=Config.TIMELEFT_TAG)

    def _setup_viewport(self):
        """Setup viewport and position window."""
        x_pos = (Config.SCREEN_WIDTH - Config.VIEWPORT_WIDTH -
                 Config.PADDING_XWIN_POS)
        y_pos = (Config.SCREEN_HEIGHT - Config.VIEWPORT_HEIGHT -
                 Config.PADDING_YWIN_POS)

        dpg.create_viewport(
            title="Timeleft View Port",
            width=Config.VIEWPORT_WIDTH,
            height=Config.VIEWPORT_HEIGHT
        )
        dpg.set_viewport_pos([x_pos, y_pos])

    def _configure_callbacks(self):
        """Configure all button callbacks."""
        dpg.set_item_callback(Config.START_TAG, self._callback_start)
        dpg.set_item_callback(Config.PAUSE_TAG, self._callback_pause)
        dpg.set_item_callback(Config.RESET_TAG, self._callback_reset)
        dpg.set_item_callback(Config.TIMELEFT_TAG, self._callback_timeleft)
        dpg.set_item_callback(Config.BACKGROUND_TAG, self._callback_change_bg)

    def _finalize_setup(self):
        """Finalize GUI setup with styling and configuration."""
        dpg.setup_dearpygui()
        dpg.bind_item_font(Config.TIMER_TAG, self.large_font)
        dpg.configure_item(
            Config.BACKGROUND_TAG,
            width=Config.VIEWPORT_WIDTH - Config.PADDING_TIMELEFT
        )
        dpg.configure_item(
            Config.TIMELEFT_TAG,
            width=Config.VIEWPORT_WIDTH - Config.PADDING_TIMELEFT
        )
        dpg.configure_item(
            Config.INPUT_TAG,
            width=Config.VIEWPORT_WIDTH - Config.PADDING_INPUT
        )
        dpg.set_primary_window("Timer Window", True)

    # Callback methods
    def _callback_start(self, sender, app_data, user_data):
        """Callback for start button."""
        # Play sound
        self.audio_manager.play_sound_async(self.audio_manager.start_sound)

        # Reset pause button label
        dpg.set_item_label(Config.PAUSE_TAG, "Pause")

        # Get input value
        input_value = dpg.get_value(Config.INPUT_TAG)

        # Start timer
        if not self.timer.start(input_value):
            dpg.set_value(Config.TIMER_TAG, "Invalid time")

    def _callback_pause(self, sender, app_data, user_data):
        """Callback for pause button."""
        # Play sound
        self.audio_manager.play_sound_async(self.audio_manager.pause_sound)

        # Toggle pause
        self.timer.pause()

        # Update button label
        label = "Resume" if self.timer.is_paused else "Pause"
        dpg.set_item_label(Config.PAUSE_TAG, label)

    def _callback_reset(self, sender, app_data, user_data):
        """Callback for reset button."""
        # Play sound
        self.audio_manager.play_sound_async(self.audio_manager.reset_sound)

        # Reset timer
        self.timer.reset()
        dpg.set_value(Config.TIMER_TAG, "00:00:00")

    def _callback_timeleft(self, sender, app_data, user_data):
        """Callback for time-left button."""
        # Play sound
        self.audio_manager.play_sound_async(self.audio_manager.timeleft_sound)

        # Get remaining time and play announcement
        remaining_time = dpg.get_value(Config.TIMER_TAG)
        self.audio_manager.play_timeleft_async(remaining_time)

    def _callback_shootgun(self, sender, app_data, user_data):
        """Callback for shoot gun button."""
        gun_prefix = dpg.get_value(Config.GUN_TAG)
        self.audio_manager.play_shootgun_async(gun_prefix)

    def _callback_weapon_select(self, sender, app_data, user_data):
        """Callback for weapon selection."""
        selected_gun = dpg.get_value(Config.GUN_TAG)
        self.audio_manager.play_weapon_deploy_async(selected_gun)

    def _callback_change_bg(self, sender, app_data, user_data):
        """Callback for change background button."""
        # Play sound
        self.audio_manager.play_sound_async(self.audio_manager.bg_sound)

        # Get new background texture
        bg_texture_path = self.asset_manager.get_background_texture_path()
        bg_texture_name = bg_texture_path.rsplit('/', 1)[-1]

        if not os.path.isfile(bg_texture_path):
            print(f"Image not found: {bg_texture_path}")
            return

        # Update texture
        width, height, channels, data = dpg.load_image(bg_texture_path)
        dpg.set_value(Config.IMAGE_TAG, data)
        dpg.configure_item(
            Config.IMAGE_TAG,
            width=Config.IMAGE_WIDTH,
            height=Config.IMAGE_HEIGHT
        )

        # Clear and redraw drawlist
        dpg.delete_item(Config.DRAWLIST_TAG, children_only=True)
        dpg.draw_image(
            Config.IMAGE_TAG,
            pmin=(0, 0),
            pmax=(Config.IMAGE_WIDTH, Config.IMAGE_HEIGHT),
            parent=Config.DRAWLIST_TAG
        )
        dpg.draw_text(
            text=bg_texture_name,
            pos=(2, Config.IMAGE_HEIGHT - 15),
            size=14,
            color=(255, 255, 255, 255),
            parent=Config.DRAWLIST_TAG
        )

    def update_timer_display(self, time_str: str):
        """
        Update timer display with new time.

        Args:
            time_str: Formatted time string to display
        """
        dpg.set_value(Config.TIMER_TAG, time_str)

    def start(self):
        """Show viewport and start the DearPyGUI event loop."""
        dpg.show_viewport()
        dpg.start_dearpygui()

    def shutdown(self):
        """Shutdown and destroy DearPyGUI context."""
        dpg.destroy_context()
