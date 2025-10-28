"""
AudioManager class for Half-Life VOX TimeLEFT application.
Handles all audio playback operations and sound sequences.
"""

import os
import random
import threading
from time import sleep
from typing import Optional
from num2words import num2words
import pygame

from libs.asset_manager import AssetManager
from libs.config import Config


class AudioManager:
    """Manages all audio playback and sound sequences."""

    def __init__(self, asset_manager: AssetManager):
        """
        Initialize the audio manager.

        Args:
            asset_manager: AssetManager instance for path building
        """
        self.asset_manager = asset_manager

        # Initialize pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        # Preload common sound paths
        self.bg_sound = asset_manager.get_sound_path("UI", "buttonclick.wav")
        self.start_sound = asset_manager.get_sound_path("buttons", "button3.wav")
        self.pause_sound = asset_manager.get_sound_path("common", "wpn_select.wav")
        self.reset_sound = asset_manager.get_sound_path("buttons", "button1.wav")
        self.timeleft_sound = asset_manager.get_sound_path("UI", "buttonclick.wav")
        self.weapon_pickup_sound = asset_manager.get_sound_path("items", "gunpickup2.wav")
        self.open_app_sound = asset_manager.get_sound_path("items", "gunpickup2.wav")

    def play_sound(self, sound_path: str):
        """
        Play a sound file synchronously using pygame.

        Args:
            sound_path: Full path to the sound file
        """
        try:
            sound = pygame.mixer.Sound(sound_path)
            channel = sound.play()
            # Wait for sound to finish
            while channel.get_busy():
                pygame.time.wait(10)
        except pygame.error as e:
            print(f"Error playing sound {sound_path}: {e}")

    def play_sound_async(self, sound_path: str):
        """
        Play a sound file asynchronously.

        Args:
            sound_path: Full path to the sound file
        """
        try:
            sound = pygame.mixer.Sound(sound_path)
            sound.play()
        except pygame.error as e:
            print(f"Error playing sound {sound_path}: {e}")

    def time_to_words(self, time_str: str) -> list:
        """
        Convert time string to list of words for VOX playback.

        Args:
            time_str: Time string in HH:MM:SS format

        Returns:
            List of word strings for audio playback
        """
        hours, minutes, seconds = map(int, time_str.split(":"))
        words = []

        if hours > 0:
            words += self._split_words(hours)
            words.append("hour" if hours == 1 else "hours")

        if minutes > 0:
            if hours > 0:
                words.append("_comma")
            words += self._split_words(minutes)
            words.append("minutes")  # No sound-bite for "singular minute"

        if seconds > 0:
            if hours > 0 or minutes > 0:
                words.append("and")
            words += self._split_words(seconds)
            words.append("second" if seconds == 1 else "seconds")

        return words

    @staticmethod
    def _split_words(hyphenated_word: int) -> list:
        """
        Split hyphenated numbers into individual words.

        Args:
            hyphenated_word: Number to convert

        Returns:
            List of individual word strings
        """
        return num2words(hyphenated_word).replace("-", " ").split()

    def play_timeleft(self, timeleft: str):
        """
        Play time-left announcement sequence.

        Args:
            timeleft: Time remaining in HH:MM:SS format
        """
        time_words = self.time_to_words(timeleft)
        time_wavs = [
            self.asset_manager.append_file_extension(word, "wav")
            for word in time_words
        ]
        time_wavs.append("remaining.wav")

        for sound_file in time_wavs:
            sound_path = self.asset_manager.build_path("sounds/vox", sound_file)
            self.play_sound(sound_path)

    def play_timeleft_async(self, timeleft: str):
        """
        Play time-left announcement asynchronously.

        Args:
            timeleft: Time remaining in HH:MM:SS format
        """
        threading.Thread(
            target=self.play_timeleft,
            args=(timeleft,),
            daemon=True
        ).start()

    def play_countdown(self):
        """Play countdown sequence (5, 4, 3, 2, 1) followed by ending sound."""
        # Play countdown
        countdown_wavs = [
            self.asset_manager.append_file_extension(word, "wav")
            for word in Config.COUNTDOWN_SOUNDS
        ]

        for sound_file in countdown_wavs:
            period_path = self.asset_manager.build_path("sounds/vox", "_period.wav")
            self.play_sound(period_path)
            sound_path = self.asset_manager.build_path("sounds/vox", sound_file)
            self.play_sound(sound_path)

        # Play ending sound
        end_sound_path = self.asset_manager.get_random_file(
            self.asset_manager.build_path(f"sounds/{Config.END_SOUND_TYPE}")
        )
        self.play_sound(end_sound_path)

    def play_countdown_async(self):
        """Play countdown sequence asynchronously."""
        threading.Thread(
            target=self.play_countdown,
            daemon=True
        ).start()

    def play_shootgun(self, gun_prefix: str):
        """
        Play weapon shooting sound.

        Args:
            gun_prefix: Gun name/prefix to play
        """
        gun_path = self.asset_manager.build_path("sounds/cs_weapons/shoot")
        gun_filenames = os.listdir(gun_path)

        # Determine if we're looking for "unsil" sounds
        is_unsil = "unsil" in gun_prefix

        # Filter sounds accordingly
        filtered_sounds = [
            gun for gun in gun_filenames
            if gun_prefix in gun and (("unsil" in gun) if is_unsil else ("unsil" not in gun))
        ]

        # Construct full paths
        gun_fullpaths = [os.path.join(gun_path, gun) for gun in filtered_sounds]

        if not gun_fullpaths:
            print("No matching gun sounds found.")
            return

        # Pick a random sound and play it
        selected_sound = random.choice(gun_fullpaths)
        self.play_sound(selected_sound)

    def play_shootgun_async(self, gun_prefix: str):
        """
        Play weapon shooting sound asynchronously.

        Args:
            gun_prefix: Gun name/prefix to play
        """
        threading.Thread(
            target=self.play_shootgun,
            args=(gun_prefix,),
            daemon=True
        ).start()

    def play_weapon_deploy(self, selected_gun: str):
        """
        Play weapon deploy sound sequence.

        Args:
            selected_gun: Selected gun name
        """
        # Weapons that have no deploy sound
        if selected_gun in Config.WEAPONS_NO_DEPLOY:
            self.play_sound_async(self.weapon_pickup_sound)
            return

        # Standard deploy sound
        gun_deploy = self.asset_manager.build_path(
            "sounds/cs_weapons/deploy",
            f"{selected_gun}_deploy.wav"
        )

        # Special handling for M4A1 bolt pull (play sequentially)
        if selected_gun in Config.WEAPONS_BOLTPULL:
            try:
                # Play deploy sound and wait
                deploy_sound = pygame.mixer.Sound(gun_deploy)
                deploy_sound.play()
                sleep(Config.BOLTPULL_DELAY)

                # Play bolt pull
                m4_boltpull = self.asset_manager.build_path(
                    "sounds/cs_weapons/deploy",
                    "m4a1_boltpull.wav"
                )
                boltpull_sound = pygame.mixer.Sound(m4_boltpull)
                boltpull_sound.play()
            except pygame.error as e:
                print(f"Error playing weapon deploy: {e}")
        else:
            # Just play deploy sound async
            self.play_sound_async(gun_deploy)

    def play_weapon_deploy_async(self, selected_gun: str):
        """
        Play weapon deploy sound asynchronously.

        Args:
            selected_gun: Selected gun name
        """
        threading.Thread(
            target=self.play_weapon_deploy,
            args=(selected_gun,),
            daemon=True
        ).start()
