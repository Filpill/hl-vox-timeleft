"""
AssetManager class for Half-Life VOX TimeLEFT application.
Handles all file operations, path building, and asset loading.
"""

import os
import random
from pathlib import Path


class AssetManager:
    """Manages asset loading and file operations."""

    def __init__(self):
        """Initialize the asset manager with root path."""
        # Go up one level from libs/ to project root
        self.root_path = Path(__file__).parent.parent
        self.assets_path = self.root_path / "assets"

    def build_path(self, path_suffix: str, file: str = "") -> str:
        """
        Build a full path to an asset file.

        Args:
            path_suffix: Relative path within assets directory
            file: Filename (optional)

        Returns:
            Full path to the asset file
        """
        path_dir = self.assets_path / path_suffix
        if file:
            return str(path_dir / file)
        return str(path_dir) + "/"

    def get_random_file(self, path: str) -> str:
        """
        Get a random file from a directory.

        Args:
            path: Directory path to choose from

        Returns:
            Full path to a random file
        """
        files = [f for f in os.listdir(path)]
        random_file = random.choice(files)
        return f"{path}{random_file}"

    def load_gun_names(self) -> list:
        """
        Load unique gun names from weapon sounds directory.

        Returns:
            Sorted list of unique gun names
        """
        gun_path = self.build_path("sounds/cs_weapons/shoot")
        files = [f.split("-")[0] for f in os.listdir(gun_path)]
        unique_guns = list(set(files))
        return sorted(unique_guns)

    def get_background_names(self) -> list:
        """
        Get all background texture filenames.

        Returns:
            Sorted list of background image filenames
        """
        bg_path = self.build_path("img/bg")
        files = sorted([f for f in os.listdir(bg_path)])
        return files

    def get_background_texture_path(self, filename: str = None) -> str:
        """
        Get a background texture path. If filename is None, returns random.

        Args:
            filename: Specific background filename (optional)

        Returns:
            Full path to a background image
        """
        bg_path = self.build_path("img/bg")
        if filename is None:
            return self.get_random_file(bg_path)
        return f"{bg_path}{filename}"

    def get_sound_path(self, category: str, filename: str) -> str:
        """
        Get path to a specific sound file.

        Args:
            category: Sound category subdirectory
            filename: Sound filename

        Returns:
            Full path to the sound file
        """
        return self.build_path(f"sounds/{category}", filename)

    def get_font_path(self, filename: str) -> str:
        """
        Get path to a font file.

        Args:
            filename: Font filename

        Returns:
            Full path to the font file
        """
        return self.build_path("fonts", filename)

    @staticmethod
    def append_file_extension(filename: str, extension: str) -> str:
        """
        Append file extension to filename.

        Args:
            filename: Base filename
            extension: File extension (without dot)

        Returns:
            Filename with extension
        """
        return f"{filename}.{extension}"
