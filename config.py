# config.py
from pathlib import Path

import toml
from xdg_base_dirs import xdg_config_home

DEFAULT_CONFIG = {"github": {"username": "terpinedream", "repo": "tuxagotchi"}}
DEFAULT_CONFIG_PATH = xdg_config_home() / "tuxagotchi.toml"


def load_config(path: Path = DEFAULT_CONFIG_PATH):
    with open(path, "r") as f:
        return toml.load(f)
