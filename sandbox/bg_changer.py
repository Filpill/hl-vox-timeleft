import dearpygui.dearpygui as dpg
from PIL import Image
from pathlib import Path
import numpy as np
import random
import os

def build_path(file, path_suffix):                 
    root_path = Path(__file__).parent              
    path_dir = f"{root_path}/assets/{path_suffix}" 
    return f"{path_dir}/{file}"                    

def get_random_file(path):                          
        files = [f for f in os.listdir(path)]       
        random_file = random.choice(files)          
        return random_file, f"{path}/{random_file}" 


def change_background(sender, app_data, user_data):
    bg_texture_name, bg_texture_path = get_random_file(build_path("", "img/bg")) 
    if not os.path.isfile(bg_texture_path):
        print(f"Image not found: {bg_texture_path}")
        return

    width, height, channels, data = dpg.load_image(bg_texture_path)

    # ✅ SAFELY update existing texture
    dpg.set_value(TEXTURE_TAG, data)
    dpg.configure_item(TEXTURE_TAG, width=width, height=height)

    # ✅ Clear and redraw drawlist
    dpg.delete_item(DRAWLIST_TAG, children_only=True)

    dpg.draw_image(TEXTURE_TAG, pmin=(50, 50), pmax=(width, height), parent=DRAWLIST_TAG)
    dpg.draw_text(text=bg_texture_name, pos=(10, height - 20), size=16, parent=DRAWLIST_TAG)

DRAWLIST_TAG = "drawlist"                                                    
TEXTURE_TAG = "image_texture"                                                
bg_texture_name, bg_texture_path = get_random_file(build_path("","img/bg"))  
width, height, channels, data = dpg.load_image(bg_texture_path)

dpg.create_context()

with dpg.texture_registry():
    dpg.add_dynamic_texture(width, height, data, tag=TEXTURE_TAG)

with dpg.viewport_drawlist(front=True, tag=DRAWLIST_TAG):
    dpg.draw_image(TEXTURE_TAG, pmin=(50, 50), pmax=(width, height))
    dpg.draw_text(text="Initial Image", pos=(10, height - 20), size=16)

with dpg.window(label="Controls"):
    dpg.add_button(label="Change Background", callback=change_background)

dpg.create_viewport(width=400, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

