import json
import os
from logic.logger import logger
from logic.app_config import app_config

# Construct an absolute path to the config file
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'config')
CONFIG_PATH = os.path.join(CONFIG_DIR, 'config.json')

def load_config():
    # Ensure the config directory exists
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    if not os.path.exists(CONFIG_PATH):
        logger.info("No config file found, creating a default one.")
        default_config = {
            "refresh_interval": 5,
            "exclude_programs": ["Ankama", "Dofus Multi Compte"],
            "theme": "dark",
            "keyboard_shortcuts": {
                "open_tab": "Ctrl+T",
                "close_tab": "Ctrl+W",
                "switch_tab_left": "Shift+Tab",
                "switch_tab_right": "Tab",
                "focus_tab_1": "F1",
                "focus_tab_2": "F2",
                "focus_tab_3": "F3",
                "focus_tab_4": "F4",
                "focus_tab_5": "F5",
                "focus_tab_6": "F6",
                "focus_tab_7": "F7",
                "focus_tab_8": "F8"
            }
        }
        save_config(default_config)
        app_config.set_config(default_config)
        return default_config
        
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            logger.info(f"Loaded config: {config}")
            # Ensure all keys are present
            if "duplicate_click_characters" not in config:
                config["duplicate_click_characters"] = []
            if "keyboard_shortcuts" not in config:
                config["keyboard_shortcuts"] = {
                    "open_tab": "Ctrl+T",
                    "close_tab": "Ctrl+W",
                    "switch_tab_left": "Shift+Tab",
                    "switch_tab_right": "Tab",
                    "focus_tab_1": "F1",
                    "focus_tab_2": "F2",
                    "focus_tab_3": "F3",
                    "focus_tab_4": "F4",
                    "focus_tab_5": "F5",
                    "focus_tab_6": "F6",
                    "focus_tab_7": "F7",
                    "focus_tab_8": "F8"
                }
            if "refresh_interval" not in config:
                config["refresh_interval"] = 5
            app_config.set_config(config)
            return config
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading config file: {e}. Returning empty config.")
        return {} # Return empty config on error

def save_config(config_data):
    try:
        # Ensure the config directory exists
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
            
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
        
        app_config.set_config(config_data)
        logger.info(f"Saved config: {config_data}")
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
