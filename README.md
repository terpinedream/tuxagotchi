# tuxagotchi
**Tuxagotchi is a TUI based tomagotchi-like pet that lives in your terminal.**

***"Feed" Tux by pushing your code to a specified repo***
****Happy = 4 hrs****
****Neutral = 2 hrs****
****Sad = 1 hrs****
****Dead = just push the code, man****

***Currently using rich for rendering***

**ASSETS**
***Stores the different ASCII art stages for Tux***
***xxx2.txt holds a duplicate file with an additional line of padding on the top***
***This is used to give the illusion of animations***

**CONFIG.TOML**
***Holds credentials**
***Username + Repo name***

**GITHUB.PY**
***Handles GitHub API interactions***

**TUX.PY**
***Holds functions for Tux's moods***

**TUXAGOTCHI.PY**
***Loads config & holds main() function***
***Checks for new commits and "animates" Tux via tick***
****Please note in line 28, the CHECK_INTERVAL NEEDS to be 60s****
****This is to prevent you from hitting the API request limit****
****Which would instantly kill Tux :(****

**UI.PY**
***Renders the TUI***
***Uses rich for rendering***
***If I can get better ASCII art/animations I will likely switch to Textual***
