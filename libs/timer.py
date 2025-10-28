"""
Timer class for Half-Life VOX TimeLEFT application.
Encapsulates timer logic and state management.
"""

import time
import threading
from typing import Callable, Optional


class Timer:
    """Manages countdown timer state and operations."""

    def __init__(self, countdown_threshold: int = 5):
        """
        Initialize the timer.

        Args:
            countdown_threshold: Seconds before playing countdown audio
        """
        self.countdown_threshold = countdown_threshold
        self._total_seconds = 0
        self._is_running = False
        self._is_paused = False
        self._reset_requested = False
        self._countdown_sound_played = False
        self._update_callback = None
        self._countdown_callback = None
        self._timer_thread = None

    @property
    def is_running(self) -> bool:
        """Check if timer is currently running."""
        return self._is_running

    @property
    def is_paused(self) -> bool:
        """Check if timer is paused."""
        return self._is_paused

    @property
    def current_time(self) -> int:
        """Get current time in seconds."""
        return self._total_seconds

    def set_update_callback(self, callback: Callable[[str], None]):
        """
        Set callback for timer updates.

        Args:
            callback: Function to call with formatted time string
        """
        self._update_callback = callback

    def set_countdown_callback(self, callback: Callable[[], None]):
        """
        Set callback for countdown trigger.

        Args:
            callback: Function to call when countdown threshold is reached
        """
        self._countdown_callback = callback

    def start(self, time_str: str) -> bool:
        """
        Start the timer with given time.

        Args:
            time_str: Time string in HH:MM:SS format

        Returns:
            True if started successfully, False otherwise
        """
        try:
            h, m, s = map(int, time_str.strip().split(":"))
            total_seconds = h * 3600 + m * 60 + s
            if total_seconds <= 0:
                return False
        except ValueError:
            return False

        # Auto-resume if paused
        self._is_paused = False
        self._reset_requested = False

        # Start timer in a new thread
        self._timer_thread = threading.Thread(
            target=self._run_timer,
            args=(total_seconds,),
            daemon=True
        )
        self._timer_thread.start()
        return True

    def pause(self):
        """Toggle pause state."""
        self._is_paused = not self._is_paused

    def resume(self):
        """Resume the timer if paused."""
        self._is_paused = False

    def reset(self):
        """Request timer reset."""
        self._reset_requested = True
        self._total_seconds = 0

    def get_formatted_time(self, seconds: Optional[int] = None) -> str:
        """
        Get formatted time string.

        Args:
            seconds: Seconds to format, or None to use current time

        Returns:
            Formatted time string in HH:MM:SS format
        """
        if seconds is None:
            seconds = self._total_seconds

        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02}:{m:02}:{s:02}"

    def _run_timer(self, total_seconds: int):
        """
        Internal method to run the timer loop.

        Args:
            total_seconds: Starting time in seconds
        """
        self._total_seconds = total_seconds
        self._is_running = True
        self._countdown_sound_played = False

        while self._total_seconds >= 0 and self._is_running:
            # Check for reset
            if self._reset_requested:
                self._reset_requested = False
                break

            # Check for pause
            if self._is_paused:
                time.sleep(0.1)
                continue

            # Update display
            formatted = self.get_formatted_time()
            if self._update_callback:
                self._update_callback(formatted)

            # Trigger countdown audio at threshold
            if (self._total_seconds == self.countdown_threshold and
                    not self._countdown_sound_played):
                self._countdown_sound_played = True
                if self._countdown_callback:
                    self._countdown_callback()

            time.sleep(1)
            self._total_seconds -= 1

        self._is_running = False

    def parse_time_string(self, time_str: str) -> Optional[int]:
        """
        Parse time string to total seconds.

        Args:
            time_str: Time string in HH:MM:SS format

        Returns:
            Total seconds or None if invalid
        """
        try:
            h, m, s = map(int, time_str.strip().split(":"))
            total_seconds = h * 3600 + m * 60 + s
            return total_seconds if total_seconds > 0 else None
        except (ValueError, AttributeError):
            return None
