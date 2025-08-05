# config.py
import tomllib


def load_config(path="config.toml"):
    with open(path, "rb") as f:
        return tomllib.load(f)
