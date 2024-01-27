import json
import os

# Define the default keybinds
DEFAULT_KEYBINDS = {
    "undo": "Ctrl+Z",
    "redo": "Ctrl+R",
    "hide_crosshair": "Ctrl+H",
    "self_destruct": "Ctrl+D",
    "offset_keybind": "Ctrl+O",
    "offset_x": 0,
    "offset_y": 0,
    "crosshair_disable_mode": 0  # Default value for the dropdown, 0 corresponds to "Disabled"
}

# Define path to the CrossPixel directory in the AppData\Local directory
appdata_local_path = os.path.join(os.path.expanduser("~"), "AppData", "Local")
CROSSPIXEL_DIR_PATH = os.path.join(appdata_local_path, "CrossPixel")
KEYBINDS_FILE_PATH = os.path.join(CROSSPIXEL_DIR_PATH, "keybinds_config.json")

def ensure_crosspixel_folder_exists():
    r"""Ensure the CrossPixel directory exists within the AppData\Local directory."""
    if not os.path.exists(CROSSPIXEL_DIR_PATH):
        try:
            os.makedirs(CROSSPIXEL_DIR_PATH)
            print("CrossPixel directory created successfully.")
        except OSError as e:
            print(f"Error creating CrossPixel directory: {e}")

def save_keybinds_to_file(keybinds):
    r"""Save keybinds to a file in the CrossPixel directory within the AppData\Local directory."""
    ensure_crosspixel_folder_exists()
    
    # Save the keybinds to the file
    with open(KEYBINDS_FILE_PATH, 'w') as file:
        json.dump(keybinds, file)

def load_keybinds_from_file():
    r"""Load keybinds from the file in the CrossPixel directory within the AppData\Local directory. 
       Return default keybinds if file doesn't exist or there's an error reading it."""
    ensure_crosspixel_folder_exists()

    # If the file doesn't exist, return default keybinds
    if not os.path.exists(KEYBINDS_FILE_PATH):
        return DEFAULT_KEYBINDS

    # If the file exists, try to load and return the keybinds
    try:
        with open(KEYBINDS_FILE_PATH, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading file: {e}")
        return DEFAULT_KEYBINDS
