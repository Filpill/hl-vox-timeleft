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
    return f"{path}{random_file}"

def load_gunnames():
    gun_path = build_path("sounds/cs_weapons/shoot", "")
    files = [f.split("-")[0] for f in os.listdir(gun_path)]
    unique_guns = list(set(files))
    return sorted(unique_guns)

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
    end_sound_path = get_random_file(build_path(f"sounds/{sound_type}",""))
    play_sound(end_sound_path)

def play_shootgun():
    gun_prefix = dpg.get_value(GUN_TAG)
    gun_path = build_path("sounds/cs_weapons/shoot", "") 

    gun_filenames = [f for f in os.listdir(gun_path)]
    gun_filenames_filtered = [gun for gun in gun_filenames if gun_prefix in gun]

    gun_fullpath = [f"{gun_path}{gun}" for gun in gun_filenames_filtered]
    gun_sound_path = random.choice(gun_fullpath)
    play_sound(gun_sound_path)

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
        if total_seconds == countdown_threshold and not countdown_sound_played:
            played_countdown = True
            threading.Thread(target=play_countdown, args=("sounds/vox",), daemon=True).start()

        time.sleep(1)
        total_seconds -= 1
    countdown_running = False #reset flag


def click_start(sender, app_data, user_data):

    global pause_requested

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(start_sound,), daemon=True).start()

    # Auto-resume if paused
    pause_requested = False
    dpg.set_item_label(PAUSE_TAG, "Pause")  # Reset label

    # Get Input value from the user-text box
    input_value = dpg.get_value(INPUT_TAG)

    # Convert text input value and map to time units to calculate total seconds remaining
    try:
        h, m, s = map(int, input_value.strip().split(":"))
        total_seconds = h * 3600 + m * 60 + s
        if total_seconds <= 0:
            raise ValueError
    except ValueError:
        dpg.set_value(TIMER_TAG, "Invalid time")
        return

    # Update the Timer on a new thread
    threading.Thread(target=update_timer, args=(total_seconds,), daemon=True).start()

def click_pause(sender, app_data, user_data):
    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(pause_sound,), daemon=True).start()

    global pause_requested
    pause_requested = not pause_requested  # Toggle pause
    dpg.set_item_label("pause_button", "Resume" if pause_requested else "Pause")

def click_reset(sender, app_data, user_data):

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(reset_sound,), daemon=True).start()

    global reset_requested
    reset_requested = True
    dpg.set_value(TIMER_TAG, "00:00:00")

def click_timeleft(sender, app_data, user_data):

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(timeleft_sound,), daemon=True).start()

    remaining_time = dpg.get_value(TIMER_TAG)
    threading.Thread(target=play_timeleft, args=(remaining_time, "sounds/vox",), daemon=True).start()

def click_shootgun(sender, app_data, user_data):                                                      
    threading.Thread(target=play_shootgun, args=(), daemon=True).start() 

def click_weapon_select(sender, app_data, user_data):                                                       
    threading.Thread(target=play_sound, args=(weapon_pickup_sound,), daemon=True).start()

def click_change_bg(sender, app_data, user_data):

    # Play sound after activating callback
    threading.Thread(target=play_sound, args=(bg_sound,), daemon=True).start()
    
    # Get new BG image
    bg_texture_path = get_random_file(build_path("img/bg",""))  
    bg_texture_name = bg_texture_path.rsplit('/', 1)[-1]
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

    # Variables
    reset_requested     = False
    pause_requested     = False
    countdown_running   = False
    countdown_threshold = 5 # Measured in seconds
    pomodorro_time      = "00:30:00" # HH:MM:SS

    screen_width      = 1920
    screen_height     = 1080
    viewport_width    = 250
    viewport_height   = 405
    image_width       = 250
    image_height      = 180
    padding_input     = 75
    padding_xwin_pos  = 10
    padding_ywin_pos  = 10
    padding_timeleft  = 15

    GUN_TAG         = "gun_tag"
    TEXT_TAG        = "text_tag"
    TIMER_TAG       = "timer_text"
    INPUT_TAG       = "input_field"
    START_TAG       = "start_button"
    PAUSE_TAG       = "pause_button"
    RESET_TAG       = "reset_button"
    IMAGE_TAG       = "image_texture"
    SHOOT_TAG       = "shoot_gun_button"
    DRAWLIST_TAG    = "drawlist_tag"
    TIMELEFT_TAG    = "timeleft_button"
    BACKGROUND_TAG  = "background_button"

    bg_texture_path      = get_random_file(build_path("img/bg",""))
    bg_sound             = build_path("sounds/UI/","buttonclick.wav")
    start_sound          = build_path("sounds/buttons/","button3.wav")
    pause_sound          = build_path("sounds/common/","wpn_select.wav")
    reset_sound          = build_path("sounds/buttons/","button1.wav")
    timeleft_sound       = build_path("sounds/UI/","buttonclick.wav")
    weapon_pickup_sound  = build_path("sounds/items/","gunpickup2.wav")
    open_app_sound       = build_path("sounds/items/","gunpickup2.wav")
    font_trebuc          = build_path("fonts","trebuc.ttf")

    # Sound to play on opening application                                              
    threading.Thread(target=play_sound, args=(open_app_sound,), daemon=True).start() 

    # Create GUI Context here
    dpg.create_context()

    # Loading Texture Asset
    width, height, channels, data = dpg.load_image(bg_texture_path) 

    # Adding assets to registry
    with dpg.font_registry():                                                              
        large_font = dpg.add_font(font_trebuc, 48)  

    with dpg.texture_registry():                                                              
        bg = dpg.add_dynamic_texture(width, height, data, tag=IMAGE_TAG)

    with dpg.viewport_drawlist(front=True, tag=DRAWLIST_TAG):
        dpg.draw_image(
            IMAGE_TAG,
            pmin=(0, 0),  # X, Y starting point
            pmax=(image_width, image_height)  # bottom-right corner
        )

        dpg.draw_text(
            text=f"{bg_texture_path.rsplit('/', 1)[-1] }",
            pos=(2, image_height-15),  # X, Y position inside the image
            size=14,  # Font size
            color=(255, 255, 255, 255)  # White text
        )

    with dpg.window(tag="Timer Window"):

        dpg.add_spacer(height=image_height-5)

        # Change BG button
        dpg.add_button(label="Change Background", tag=BACKGROUND_TAG, callback=click_change_bg)

        # Shoot Gun Button
        with dpg.group(horizontal=True):
            with dpg.group(horizontal=False):
                dpg.add_text("Select Gun")
                dpg.add_combo(tag=GUN_TAG, default_value="glock18", items=load_gunnames(), callback=click_weapon_select, width=100)
            dpg.add_button(label="Fire", tag=SHOOT_TAG, callback=click_shootgun, height=45, width=127)

        # Countdown Timer
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=30)
            dpg.add_text("00:00:00", tag=TIMER_TAG)

        dpg.add_spacer(height=10)

        # Time input field
        dpg.add_input_text(label="HH:MM:SS", hint="HH:MM:SS", default_value=pomodorro_time, tag=INPUT_TAG)

        # Start/Pause/Reset Buttons
        with dpg.group(horizontal=True):
            dpg.add_button(label="Start Timer", tag=START_TAG)
            dpg.add_button(label="Pause", tag=PAUSE_TAG)
            dpg.add_button(label="Reset Timer", tag=RESET_TAG)

        # Timeleft Button
        dpg.add_button(label="Timeleft", tag=TIMELEFT_TAG)

    
    # Positioning window upon opening application
    x_pos = screen_width - viewport_width - padding_xwin_pos  
    y_pos = screen_height - viewport_height - padding_ywin_pos

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
    dpg.set_primary_window("Timer Window", True)
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
