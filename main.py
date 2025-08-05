import sys
from pathlib import Path

import click
import toml

from config import DEFAULT_CONFIG, DEFAULT_CONFIG_PATH, load_config
from textual_app.app import TuxApp


@click.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to the config file.",
)
def main(config: Path):
    try:
        if config is None:
            config = load_config()
        else:
            config = load_config(config)
    except FileNotFoundError as e:
        with open(DEFAULT_CONFIG_PATH, "w", encoding="UTF-8") as f:
            toml.dump(DEFAULT_CONFIG, f)
        print(f"Created default config file at {DEFAULT_CONFIG_PATH}")
        print("You should probably change the default values")
        sys.exit(0)
    app = TuxApp(config)
    app.run()


if __name__ == "__main__":
    main()
