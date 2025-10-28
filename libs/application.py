"""
Application class for Half-Life VOX TimeLEFT.
Orchestrates all components and manages the application lifecycle.
"""

import dearpygui.dearpygui as dpg

from libs.config import Config
from libs.asset_manager import AssetManager
from libs.timer import Timer
from libs.audio_manager import AudioManager
from libs.ui_manager import UIManager
from libs.clickstream_tracker import ClickstreamTracker


class Application:
    """Main application class that orchestrates all components."""

    def __init__(self):
        """Initialize the application and all its components."""
        # Initialize components
        self.asset_manager = AssetManager()
        self.timer = Timer(countdown_threshold=Config.COUNTDOWN_THRESHOLD)
        self.audio_manager = AudioManager(self.asset_manager)

        # Initialize clickstream tracker
        self.clickstream_tracker = ClickstreamTracker(
            project_id=Config.CLICKSTREAM_PROJECT_ID,
            dataset_id=Config.CLICKSTREAM_DATASET_ID,
            table_id=Config.CLICKSTREAM_TABLE_ID,
            batch_size=Config.CLICKSTREAM_BATCH_SIZE,
            enabled=Config.CLICKSTREAM_ENABLED
        )

        self.ui_manager = UIManager(
            self.asset_manager,
            self.audio_manager,
            self.timer,
            self.clickstream_tracker
        )

        # Wire up callbacks
        self._setup_callbacks()

    def _setup_callbacks(self):
        """Setup callbacks between components."""
        # Timer update callback
        self.timer.set_update_callback(self.ui_manager.update_timer_display)

        # Timer countdown callback
        self.timer.set_countdown_callback(self.audio_manager.play_countdown_async)

    def run(self):
        """Run the application."""
        # Play startup sound
        self.audio_manager.play_sound_async(self.audio_manager.open_app_sound)

        # Track application start
        self.clickstream_tracker.track_event("app_start", "application")

        # Initialize and start GUI
        self.ui_manager.initialize_gui()
        self.ui_manager.start()

        # Cleanup
        self.ui_manager.shutdown()
        self.clickstream_tracker.shutdown()


def main():
    """Main entry point for the application."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
