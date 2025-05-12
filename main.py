import time
import threading
import subprocess
import dearpygui.dearpygui as dpg
from num2words import num2words
from pathlib import Path

def build_sound_path(sound_file, dir):
    root_path = Path(__file__).parent
    sound_dir = f"{root_path}/{dir}"
    return f"{sound_dir}/{sound_file}"

def play_sound(sound_file, dir):
    sound_path = build_sound_path(sound_file, dir)
    subprocess.run(["bash", "-c", f"ffplay -nodisp -autoexit {sound_path}"], capture_output=True)

def append_file_extension(sound_name, ext):
    return f"{sound_name}.{ext}"

def play_countdown(dir):
    countdown_list = [
        "ten","nine","eight","seven","six",
        "five","four","three","two","one",
    ]

    countdown_wavs  = [append_file_extension(word, "wav") for word in countdown_list]
    for sound_file in countdown_wavs:
        play_sound(sound_file, dir)
        play_sound("_period.wav", dir)

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

#--------------------------------------------------------------------------------#

def update_timer(total_seconds):
    global countdown_running
    countdown_running = True
    while total_seconds >= 0 and countdown_running and dpg.is_dearpygui_running():
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        formatted = f"{h:02}:{m:02}:{s:02}"
        dpg.set_value(TIMER_TAG, formatted)
        time.sleep(1)
        total_seconds -= 1
    countdown_running = False

def on_start(sender, app_data, user_data):
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

def apply_font(tag):
    dpg.bind_item_font(tag, large_font)

#--------------------------------------------------------------------------------#

if __name__ == "__main__":
    # play_countdown("vox")
    # timeleft = "07:46:19"
    # play_timeleft(timeleft, "vox")
    
    dpg.create_context()

    with dpg.font_registry():                                                             
        large_font = dpg.add_font(f"{Path(__file__).parent}/assets/fonts/trebuc.ttf", 48) 

    TIMER_TAG = "timer_text"
    INPUT_TAG = "input_field"
    BUTTON_TAG = "start_button"

    countdown_running = False

    with dpg.window(tag="Timer Window"):#, width=250, height=200):
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=25)
            dpg.add_text("00:00:00", tag=TIMER_TAG)

        dpg.add_spacer(height=20)

        # Time input field
        dpg.add_input_text(label="HH:MM:SS", hint="HH:MM:SS", default_value="00:30:00", width=150, tag=INPUT_TAG)

        # Start button
        dpg.add_button(label="Start Timer", tag=BUTTON_TAG)

    viewport_width  = 250
    viewport_height = 150
    screen_width    = 1920
    screen_height   = 1080
    x_padding = 25
    x_pos           = screen_width - viewport_width - x_padding
    y_pos           = screen_height - viewport_height
    dpg.create_viewport(title="Timeleft View Port", width=viewport_width, height=viewport_height)
    dpg.set_viewport_pos([x_pos,y_pos])

    #threading.Thread(target=update_timer, daemon=True).start()
    dpg.set_item_callback(BUTTON_TAG, on_start)

    dpg.setup_dearpygui()
    apply_font(TIMER_TAG)
    dpg.show_viewport()
    dpg.set_primary_window("Timer Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
