import subprocess
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


def play_remaining_time(remaining_time, dir):
    time_words = time_to_words(remaining_time)
    time_wavs  = [append_file_extension(word, "wav") for word in time_words]
    time_wavs += ["remaining.wav"]
    print(time_wavs)

    for sound_file in time_wavs:
        play_sound(sound_file, dir)

play_countdown("vox")

remaining_time = "07:46:19"
play_remaining_time(remaining_time, "vox")