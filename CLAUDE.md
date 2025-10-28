# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HL-VOX-TimeLEFT is a Half-Life themed Pomodoro timer built with Python and DearPyGUI. It features VOX (voice) announcements, weapon sounds, rotating Half-Life sky textures, and a countdown timer with full audio integration.

## System Requirements

**ffmpeg** must be installed for audio playback via `ffplay`:
```bash
# Arch Linux
sudo pacman -S ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

## Environment Setup

This project uses **uv** package manager (Python 3.12+):

```bash
# Create virtual environment
uv venv --python 3.12

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync

# Add new package
uv add <package-name>

# Compile requirements.txt from pyproject.toml
uv pip compile pyproject.toml > requirements.txt
```

## Running the Application

```bash
python3 main.py
```

The application will:
1. Play startup sound
2. Open GUI in bottom-right corner of screen
3. Display rotating Half-Life background textures
4. Allow timer control via Start/Pause/Reset buttons

## Architecture Overview

This codebase follows an **object-oriented architecture** with clear separation of concerns. All core classes are organized in the `libs/` directory:

### Core Components

```
main.py
    └── Application (libs/application.py)
            ├── Config (libs/config.py) - Constants and configuration
            ├── AssetManager (libs/asset_manager.py) - File and asset loading
            ├── Timer (libs/timer.py) - Timer logic and state
            ├── AudioManager (libs/audio_manager.py) - Sound playback
            └── UIManager (libs/ui_manager.py) - GUI and event handling
```

### Component Responsibilities

**Config** - Centralized constants (no instantiation needed)
- Screen/viewport dimensions
- UI padding values
- DearPyGUI tag identifiers
- Timer settings (default time, countdown threshold)

**AssetManager** - All file operations
- Builds paths to assets directory (`assets/sounds/`, `assets/img/`, `assets/fonts/`)
- Random file selection for backgrounds and ending sounds
- Loads weapon names from sound files
- Path resolution for fonts, textures, and audio

**Timer** - Countdown logic (thread-safe)
- State: `is_running`, `is_paused`, `current_time`
- Runs countdown in daemon thread
- Callback-based notifications (update display, trigger countdown)
- Parses HH:MM:SS format strings
- Handles pause/resume/reset

**AudioManager** - All audio playback
- Synchronous and asynchronous playback via `ffplay`
- Sound sequences: countdown (5-4-3-2-1), time-left announcements, weapon sounds
- Converts time to VOX words using `num2words` library
- Special weapon handling (M4A1 boltpull, deploy sounds)
- Preloads common sound paths on initialization

**UIManager** - DearPyGUI interface
- Creates all GUI elements (buttons, timer display, weapon selector)
- Manages background texture rotation
- Event callbacks wired to business logic
- Updates timer display via callback from Timer class
- Handles font registration and viewport positioning

**Application** - Orchestration
- Initializes all components in correct order
- Wires callbacks between Timer → UIManager and Timer → AudioManager
- Manages application lifecycle (startup sound → GUI loop → cleanup)

### Key Design Patterns

**Observer Pattern (via callbacks)**
- Timer doesn't know about UI, but notifies via `set_update_callback()`
- Timer triggers audio countdown via `set_countdown_callback()`
- Loose coupling between components

**Dependency Injection**
- UIManager receives AssetManager, AudioManager, Timer via constructor
- AudioManager receives AssetManager
- Application wires everything together

**Thread Safety**
- No global variables (refactored from 15+ globals)
- Timer uses instance variables for state
- Audio playback in daemon threads

## Asset Structure

```
assets/
├── fonts/trebuc.ttf - Trebuchet MS font for timer display
├── img/
│   ├── bg/ - Half-Life sky textures (randomly rotated)
│   └── model/ - T/CT squad images
└── sounds/
    ├── buttons/ - UI button sounds
    ├── common/ - Generic sounds (wpn_select)
    ├── cs_weapons/
    │   ├── deploy/ - Weapon equip sounds
    │   └── shoot/ - Weapon firing sounds (format: gunname-N.wav)
    ├── fvox/ - Half-Life VOX system
    ├── gman/ - G-Man quotes (ending sounds)
    ├── items/ - Item pickup sounds
    ├── UI/ - UI interaction sounds
    └── vox/ - Time announcement words (one.wav, two.wav, minutes.wav, etc.)
```

## Special Audio Behavior

**Weapon Sounds**
- Weapon names parsed from filenames in `cs_weapons/shoot/` (format: `gunname-N.wav`)
- Some weapons have "unsil" variants (silenced vs unsilenced)
- Special handling:
  - M4A1: plays deploy + boltpull with 0.4s delay
  - Deagle/Flashbang: plays generic pickup sound instead of deploy

**Time Announcements**
- Time converted to words via `num2words` library
- Hyphenated numbers split into individual words (e.g., "twenty-one" → ["twenty", "one"])
- Format: `[hours] hour(s), [minutes] minutes, and [seconds] second(s) remaining`
- Each word played as `{word}.wav` from `vox/` directory

**Countdown Sequence**
- Triggers at `Config.COUNTDOWN_THRESHOLD` seconds (default: 5)
- Plays "_period.wav" before each number
- Ends with random G-Man quote from `sounds/gman/`

## Threading Model

- **Main Thread**: DearPyGUI event loop
- **Daemon Threads**: Audio playback, timer countdown
- All audio plays asynchronously via `*_async()` methods
- Timer update callback runs on timer thread, updates GUI via DearPyGUI (thread-safe)

## Modifying Components

**Add new sound sequence**: Extend `AudioManager` in `libs/audio_manager.py`
**Add new timer mode**: Subclass or extend `Timer` class in `libs/timer.py`
**Change UI layout**: Modify `UIManager._create_main_window()` in `libs/ui_manager.py`
**Add new configuration**: Add constant to `Config` class in `libs/config.py`
**Change asset paths**: Modify `AssetManager` path-building logic in `libs/asset_manager.py`

## Important Notes

- DearPyGUI uses tag-based element access (all tags defined in `Config`)
- Background textures are dynamic textures that can be updated at runtime
- Font must be applied after `dpg.setup_dearpygui()` is called
- Viewport positioning assumes 1920x1080 screen (bottom-right corner)
- All paths built relative to project root using `Path(__file__).parent`
