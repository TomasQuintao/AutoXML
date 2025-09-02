import os
import configparser
from platformdirs import user_data_dir

def getModel():
    config_dir = user_data_dir('Config', 'AutoXML')
    config_path = os.path.join(config_dir, 'config.ini')

    if not os.path.exists(config_path):
        raise FileNotFoundError("Config file not found. Please set a default model using set command.")

    config = configparser.ConfigParser()
    config.read(config_path)

    if "Models" not in config or "default" not in config["Models"]:
        raise ValueError("Default model is not set in config. Please set one using set command.")

    return config["Models"]["default"]
