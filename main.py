"""
Half-Life VOX TimeLEFT - Pomodoro Timer Application
Main entry point for the refactored OOP version.

This application has been refactored from a 379-line procedural script
into a well-structured object-oriented architecture with the following components:

- Config: Centralized configuration and constants
- AssetManager: File operations and asset loading
- Timer: Timer logic and state management
- AudioManager: Sound playback and sequences
- UIManager: GUI creation and event handling
- Application: Component orchestration and lifecycle management
"""

from libs.application import main

if __name__ == "__main__":
    main()
