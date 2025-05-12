import time
import threading
import subprocess
import dearpygui.dearpygui as dpg
from num2words import num2words
from pathlib import Path

def build_sound_path(sound_file, dir):
    root_path = Path(__file__).parent
    sound_dir = f"{root_path}/assets/sounds/{dir}"
    return f"{sound_dir}/{sound_file}"

def play_sound(sound_file, dir):
    sound_path = build_sound_path(sound_file, dir)
    subprocess.run(["bash", "-c", f"ffplay -nodisp -autoexit {sound_path}"], capture_output=True)

def append_file_extension(sound_name, ext):
    return f"{sound_name}.{ext}"

def split_words(hypthenated_word):
    return num2words(hypthenated_word).replace("-", " ").split()

def time_to_words(time_str):
    hours, minutes, seconds = map(int, time_str.split(":"))
    
    words = []
    
    if hours > 0:
        words += split_words(hours)
        words.append("hour" if hours == 1 else "hours")
    
    if minutes > 0:
        if hours > 0:
            words.append("_comma")
        words += split_words(minutes)
        words.append("minutes") # No sound-bite for "singular minute"
    
    if seconds > 0:
        if hours > 0 or minutes > 0:
            words.append("and")
        words += split_words(seconds)
        words.append("second" if seconds == 1 else "seconds")

    return words


def play_timeleft(timeleft, dir):
    time_words = time_to_words(timeleft)
    time_wavs  = [append_file_extension(word, "wav") for word in time_words]
    time_wavs += ["remaining.wav"]
    print(time_wavs)

    for sound_file in time_wavs:
        play_sound(sound_file, dir)

def play_countdown(dir):
    countdown_list = [
        "ten","nine","eight","seven","six",
        "five","four","three","two","one",
    ]

    countdown_wavs  = [append_file_extension(word, "wav") for word in countdown_list]
    for sound_file in countdown_wavs:
        play_sound(sound_file, dir)
        play_sound("_period.wav", dir)

#--------------------------------------------------------------------------------#

def update_timer(total_seconds):
    global countdown_running, pause_requested, reset_requested
    countdown_running = True
    countdown_sound_played  = False

    while total_seconds >= 0 and countdown_running and dpg.is_dearpygui_running():

        if reset_requested:
            reset_requested = False
            break

        if pause_requested:
            time.sleep(0.1)
            continue


        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        formatted = f"{h:02}:{m:02}:{s:02}"
        dpg.set_value(TIMER_TAG, formatted)

        # Trigger countdown audio at 10s remaining
        if total_seconds == 10 and not countdown_sound_played:
            played_countdown = True
            threading.Thread(target=play_countdown, args=("vox",), daemon=True).start()

        time.sleep(1)
        total_seconds -= 1
    countdown_running = False #reset flag

def click_start(sender, app_data, user_data):
    if countdown_running:
        return  # Prevent multiple timers

    input_value = dpg.get_value(INPUT_TAG)

    try:
        h, m, s = map(int, input_value.strip().split(":"))
        total_seconds = h * 3600 + m * 60 + s
        if total_seconds <= 0:
            raise ValueError
    except ValueError:
        dpg.set_value(TIMER_TAG, "Invalid time")
        return

    threading.Thread(target=update_timer, args=(total_seconds,), daemon=True).start()

def click_pause(sender, app_data, user_data):
    global pause_requested
    pause_requested = not pause_requested  # Toggle pause
    dpg.set_item_label("pause_button", "Resume" if pause_requested else "Pause")

def click_reset(sender, app_data, user_data):
    global reset_requested
    reset_requested = True
    dpg.set_value(TIMER_TAG, "00:00:00")

def click_timeleft(sender, app_data, user_data):
    remaining_time = dpg.get_value(TIMER_TAG)
    play_timeleft(remaining_time, "vox")

def apply_font(tag):
    dpg.bind_item_font(tag, large_font)

#--------------------------------------------------------------------------------#

if __name__ == "__main__":

    dpg.create_context()

    with dpg.font_registry():                                                             
        large_font = dpg.add_font(f"{Path(__file__).parent}/assets/fonts/trebuc.ttf", 48) 

    TIMER_TAG    = "timer_text"
    INPUT_TAG    = "input_field"
    START_TAG    = "start_button"
    PAUSE_TAG    = "pause_button"
    RESET_TAG    = "reset_button"
    TIMELEFT_TAG = "timeleft_button"

    countdown_running = False
    with dpg.window(tag="Timer Window"):#, width=250, height=200):
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=30)
            dpg.add_text("00:00:00", tag=TIMER_TAG)

        dpg.add_spacer(height=10)

        # Time input field
        dpg.add_input_text(label="HH:MM:SS", hint="HH:MM:SS", default_value="00:30:00", tag=INPUT_TAG)

        # Start button
        with dpg.group(horizontal=True):
            dpg.add_button(label="Start Timer", tag=START_TAG)
            dpg.add_button(label="Pause", tag=PAUSE_TAG)
            dpg.add_button(label="Reset Timer", tag=RESET_TAG)

        # Time Left Button
        dpg.add_spacer(height=1)
        dpg.add_button(label="Timeleft", tag=TIMELEFT_TAG)

    viewport_width  = 250
    viewport_height = 180
    screen_width    = 1920
    screen_height   = 1080
    x_padding       = 25
    x_pos           = screen_width - viewport_width - x_padding
    y_pos           = screen_height - viewport_height
    dpg.create_viewport(title="Timeleft View Port", width=viewport_width, height=viewport_height)
    dpg.set_viewport_pos([x_pos,y_pos])

    dpg.set_item_callback(START_TAG, click_start)
    dpg.set_item_callback(PAUSE_TAG, click_pause)
    dpg.set_item_callback(RESET_TAG, click_reset)
    dpg.set_item_callback(TIMELEFT_TAG, click_timeleft)

    dpg.setup_dearpygui()
    apply_font(TIMER_TAG)
    dpg.configure_item(TIMELEFT_TAG, width = viewport_width-15)
    dpg.configure_item(INPUT_TAG, width = viewport_width-75)
    dpg.show_viewport()
    dpg.set_primary_window("Timer Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
