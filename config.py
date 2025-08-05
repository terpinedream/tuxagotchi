import toml


def load_config():
    config = toml.load("config.toml")
    # Provide fallback defaults for colors
    colors = config.get("colors", {})
    config["colors"] = {
        "accent": colors.get("accent", "cyan"),
        "background": colors.get("background", "black"),
        "foreground": colors.get("foreground", "white"),
        "highlight": colors.get("highlight", "yellow"),
        "todo_border": colors.get("todo_border", "green"),
    }
    return config
