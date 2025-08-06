# Tuxagotchi (Textual Edition)

Tuxagotchi is a terminal-based companion that thrives on your GitHub activity.  
This version is a full refactor using [Textual](https://textual.textualize.io/), providing a responsive and animated terminal UI featuring a commit-based mood system, interactive TODO list, and a real-time audio visualizer powered by [Cava](https://github.com/karlstav/cava).

![Screenshot](screenshots/textural/screenshot_06082025_030742.jpg)

---

## Features

- ASCII-rendered Tux avatar that reacts to your GitHub commit history and displays animated emotional states
- Mood-based animation system using 6 ASCII frames (2 per mood: ecstatic, neutral, angry)
- Countdown timer indicating when Tux will become hungry again
- Interactive TODO list with vim motions
- Real-time audio visualizer integration using Cava
- Customizable and modular architecture using Textual's widget system
- Keybind hint bar at the bottom for user guidance

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/terpinedream/tuxagotchi.git
   cd tuxagotchi
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install external dependencies:**

   - **Cava** is required for the audio visualizer:
     - Arch Linux:
       ```bash
       sudo pacman -S cava
       ```
     - Debian/Ubuntu:
       ```bash
       sudo apt install cava
       ```
     - Or [build from source](https://github.com/karlstav/cava#installation)

4. **Create a `config.toml` file** in the root directory with the following structure:
   ```toml
   [github]
   username = "your-github-username"
   repo = "your-repo-name"
   token = "your-repo-token"
   ```

---

## Running the Application

```bash
python3 -m textual_app.app
```

---

## Author

Maintained by [@terpinedream](https://github.com/terpinedream)

