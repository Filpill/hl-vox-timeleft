"""
Configuration class for Half-Life VOX TimeLEFT application.
Centralizes all constants and configuration settings.
"""

class Config:
    """Central configuration for the TimeLEFT application."""

    # Screen dimensions
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080

    # Viewport dimensions
    VIEWPORT_WIDTH = 250
    VIEWPORT_HEIGHT = 405

    # Image dimensions
    IMAGE_WIDTH = 250
    IMAGE_HEIGHT = 180

    # UI padding
    PADDING_INPUT = 75
    PADDING_XWIN_POS = 10
    PADDING_YWIN_POS = 10
    PADDING_TIMELEFT = 15

    # Timer settings
    DEFAULT_POMODORO_TIME = "00:30:00"  # HH:MM:SS
    COUNTDOWN_THRESHOLD = 5  # seconds before playing countdown

    # DearPyGUI Tags
    GUN_TAG = "gun_tag"
    TEXT_TAG = "text_tag"
    TIMER_TAG = "timer_text"
    INPUT_TAG = "input_field"
    START_TAG = "start_button"
    PAUSE_TAG = "pause_button"
    RESET_TAG = "reset_button"
    IMAGE_TAG = "image_texture"
    SHOOT_TAG = "shoot_gun_button"
    DRAWLIST_TAG = "drawlist_tag"
    TIMELEFT_TAG = "timeleft_button"
    BACKGROUND_TAG = "background_combo"

    # Sound types
    COUNTDOWN_SOUNDS = ["five", "four", "three", "two", "one"]
    END_SOUND_TYPE = "gman"

    # Special weapon handling
    WEAPONS_NO_DEPLOY = ["deagle", "flashbang"]
    WEAPONS_BOLTPULL = ["m4a1", "m4a1_unsil"]
    BOLTPULL_DELAY = 0.4  # seconds

    # BigQuery Clickstream Settings
    CLICKSTREAM_ENABLED = True  # Set to False to disable tracking
    CLICKSTREAM_PROJECT_ID = "experiment-476518"
    CLICKSTREAM_DATASET_ID = "hl_timeleft"
    CLICKSTREAM_TABLE_ID = "clickstream"
    CLICKSTREAM_BATCH_SIZE = 10  # Number of events to batch before inserting
