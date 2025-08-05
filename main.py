import sys

import toml

from config import DEFAULT_CONFIG, DEFAULT_CONFIG_PATH, load_config
from textual_app.app import TuxApp

if __name__ == "__main__":
    # TODO: read config dir from flags
    try:
        config = load_config()
    except FileNotFoundError as e:
        with open(DEFAULT_CONFIG_PATH, "w", encoding="UTF-8") as f:
            toml.dump(DEFAULT_CONFIG, f)
        print(f"Created default config file at {DEFAULT_CONFIG_PATH}")
        print("You should probably change the default values")
        sys.exit(0)
    app = TuxApp(config)
    app.run()
