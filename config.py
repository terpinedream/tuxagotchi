import toml


def load_config():
    config = toml.load("config.toml")
    # Provide fallback defaults for colors
    colors = config.get("colors", {})
    config["colors"] = {
        "accent": colors.get("accent", "red"),
        "background": colors.get("background", "transparent"),
        "foreground": colors.get("foreground", "red"),
        "highlight": colors.get("highlight", "red"),
        "todo_border": colors.get("todo_border", "red"),
    }
    return config
