from datetime import datetime


def get_last_pacman_update_time():
    log_path = "/var/log/pacman.log"
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line in reversed(lines):
            if "starting full system upgrade" in line.lower():
                # Extract the timestamp inside brackets
                timestamp_str = line.split("]")[0].strip("[")
                # Pacman logs often use: [2025-08-10T14:22:36+0000]
                try:
                    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S%z")
                except ValueError:
                    # Fallback for older formats: [2025-08-10 14:22]
                    try:
                        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        return None
    except FileNotFoundError:
        return None

    return None
