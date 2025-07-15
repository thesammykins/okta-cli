import os
import configparser

CONFIG_DIR = os.path.expanduser("~/.okta")
CONFIG_FILE = os.path.join(CONFIG_DIR, "credentials")

def get_config():
    """Reads the configuration file and returns a config object."""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def write_config(config):
    """Writes the configuration object to the config file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)
