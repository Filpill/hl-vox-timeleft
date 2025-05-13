import os
import time
import random
import threading
import subprocess
import dearpygui.dearpygui as dpg
from num2words import num2words
from pathlib import Path

def build_path(path_suffix, file):
    root_path = Path(__file__).parent
    path_dir = f"{root_path}/assets/{path_suffix}"
    return f"{path_dir}/{file}"

def play_sound(sound_path):
    subprocess.run(["bash", "-c", f"ffplay -nodisp -autoexit {sound_path}"], capture_output=True)

def append_file_extension(filename, extension):
    return f"{filename}.{extension}"

def split_words(hypthenated_word):
    return num2words(hypthenated_word).replace("-", " ").split()

def get_random_file(path):
        files = [f for f in os.listdir(path)]
        random_file = random.choice(files) 
        return random_file, f"{path}/{random_file}"

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

    for sound_file in time_wavs:
        play_sound(build_path(dir, sound_file))

def play_countdown(dir):
    countdown_list = [
        #"eleven","ten","nine","eight","seven","six",
        "five","four","three","two","one",
    ]

    # Play Countdown
    countdown_wavs  = [append_file_extension(word, "wav") for word in countdown_list]
    for sound_file in countdown_wavs:
        play_sound(build_path(dir, "_period.wav"))
        play_sound(build_path(dir, sound_file))

    # Ending Sound
    sound_type = "gman"
    end_sound, end_sound_path = get_random_file(build_path(f"sounds/{sound_type}",""))
    play_sound(end_sound_path)

#--------------------------------------------------------------------------------#

def update_timer(total_seconds):
    global countdown_running, pause_requested, reset_requested
    countdown_running = True
    countdown_sound_played  = False

    while total_seconds >= 0 and countdown_running and dpg.is_dearpygui_running():

        #if reset_requested:
        #    reset_requested = False
        #    break

        #if pause_requested:
        #    time.sleep(0.1)
        #    continue


        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        formatted = f"{h:02}:{m:02}:{s:02}"
        dpg.set_value(TIMER_TAG, formatted)

        # Trigger countdown audio at 10s remaining
        if total_seconds == countdown_threshold and not countdown_sound_played:
            played_countdown = True
            threading.Thread(target=play_countdown, args=("sounds/vox",), daemon=True).start()

        time.sleep(1)
        total_seconds -= 1
    countdown_running = False #reset flag

def click_start(sender, app_data, user_data):

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(button_click_path,), daemon=True).start()

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
    #
    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(button_click_path,), daemon=True).start()

    global pause_requested
    pause_requested = not pause_requested  # Toggle pause
    dpg.set_item_label("pause_button", "Resume" if pause_requested else "Pause")

def click_reset(sender, app_data, user_data):

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(button_click_path,), daemon=True).start()

    global reset_requested
    reset_requested = True
    dpg.set_value(TIMER_TAG, "00:00:00")

def click_timeleft(sender, app_data, user_data):

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(button_click_path,), daemon=True).start()

    remaining_time = dpg.get_value(TIMER_TAG)
    threading.Thread(target=play_timeleft, args=(remaining_time, "sounds/vox",), daemon=True).start()

def click_change_bg(sender, app_data, user_data):

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(button_click_path,), daemon=True).start()
    
    # Get new BG image
    bg_texture_name, bg_texture_path = get_random_file(build_path("img/bg",""))  
    if not os.path.isfile(bg_texture_path):                                       
        print(f"Image not found: {bg_texture_path}")                              
        return                                                                    

    # Update existing texture                                 
    width, height, channels, data = dpg.load_image(bg_texture_path)
    dpg.set_value(IMAGE_TAG, data)                            
    dpg.configure_item(IMAGE_TAG, width=image_width, height=image_height) 

    # Clear old drawlist
    dpg.delete_item(DRAWLIST_TAG, children_only=True)

    # Redraw drawlist elemnents
    dpg.draw_image(IMAGE_TAG, pmin=(0, 0), pmax=(image_width, image_height), parent=DRAWLIST_TAG)
    dpg.draw_text(text=bg_texture_name,pos=(2, image_height - 15), size=14, color=(255, 255, 255, 255),parent=DRAWLIST_TAG)

def apply_font(tag):
    dpg.bind_item_font(tag, large_font)

#--------------------------------------------------------------------------------#

if __name__ == "__main__":

    countdown_running = False  # Init default value
    countdown_threshold = 5    # Measured in seconds

    screen_width      = 1920
    screen_height     = 1080
    viewport_width    = 250
    viewport_height   = 375
    image_width       = 250
    image_height      = 180
    padding_input     = 75
    padding_xwin_pos  = 10
    padding_timeleft  = 15

    TEXT_TAG        = "text_tag"
    TIMER_TAG       = "timer_text"
    INPUT_TAG       = "input_field"
    START_TAG       = "start_button"
    PAUSE_TAG       = "pause_button"
    RESET_TAG       = "reset_button"
    IMAGE_TAG       = "image_texture"
    DRAWLIST_TAG    = "drawlist_tag"
    TIMELEFT_TAG    = "timeleft_button"
    BACKGROUND_TAG  = "background_button"

    bg_texture_name, bg_texture_path = get_random_file(build_path("img/bg",""))
    button_click_path = build_path("sounds/UI/","buttonclick.wav")
    font_trebuc_path  = build_path("fonts","trebuc.ttf")

    dpg.create_context()

    # Loading Texture Asset
    width, height, channels, data = dpg.load_image(bg_texture_path) 

    # Adding assets to registry
    with dpg.font_registry():                                                              
        large_font = dpg.add_font(font_trebuc_path, 48)  

    with dpg.texture_registry():                                                              
        bg = dpg.add_dynamic_texture(width, height, data, tag=IMAGE_TAG)

    with dpg.viewport_drawlist(front=True, tag=DRAWLIST_TAG):
        dpg.draw_image(
            IMAGE_TAG,
            pmin=(0, 0),  # X, Y starting point
            pmax=(image_width, image_height)  # bottom-right corner
        )

        dpg.draw_text(
            text=f"{bg_texture_name}",
            pos=(2, image_height-15),  # X, Y position inside the image
            size=14,  # Font size
            color=(255, 255, 255, 255)  # White text
        )

    with dpg.window(tag="Timer Window"):

        dpg.add_spacer(height=image_height)

        # Change BG button
        dpg.add_button(label="Change Background", tag=BACKGROUND_TAG, callback=click_change_bg)

        # Countdown Timer
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=30)
            dpg.add_text("00:00:00", tag=TIMER_TAG)

        dpg.add_spacer(height=10)

        # Time input field
        dpg.add_input_text(label="HH:MM:SS", hint="HH:MM:SS", default_value="00:00:05", tag=INPUT_TAG)

        # Start/Pause/Reset Buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="Start Timer", tag=START_TAG)
            dpg.add_button(label="Pause", tag=PAUSE_TAG)
            dpg.add_button(label="Reset Timer", tag=RESET_TAG)

        # Timeleft Button
        dpg.add_spacer(height=1)
        dpg.add_button(label="Timeleft", tag=TIMELEFT_TAG)

    
    # Positioning window upon opening application
    x_pos = screen_width - viewport_width - padding_xwin_pos  
    y_pos = screen_height - viewport_height

    # Creating Viewport
    dpg.create_viewport(title="Timeleft View Port", width=viewport_width, height=viewport_height)
    dpg.set_viewport_pos([x_pos,y_pos])

    # Item callbacks
    dpg.set_item_callback(START_TAG, click_start)
    dpg.set_item_callback(PAUSE_TAG, click_pause)
    dpg.set_item_callback(RESET_TAG, click_reset)
    dpg.set_item_callback(TIMELEFT_TAG, click_timeleft)
    dpg.set_item_callback(BACKGROUND_TAG, click_change_bg)

    # Setting Up GUI
    dpg.setup_dearpygui()
    apply_font(TIMER_TAG)
    dpg.configure_item(BACKGROUND_TAG, width = viewport_width-padding_timeleft)
    dpg.configure_item(TIMELEFT_TAG, width = viewport_width-padding_timeleft)
    dpg.configure_item(INPUT_TAG, width = viewport_width-padding_input)
    dpg.show_viewport()
    dpg.set_primary_window("Timer Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()
