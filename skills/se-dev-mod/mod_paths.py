"""
Shared path helpers for the mod skill.

All persistent mod data lives under the Data junction inside the skill folder.
The junction is created by Prepare.bat and points at %USERPROFILE%\\.se-dev\\mod.

Steam workshop content is read directly from its Steam folder rather than
symlinked into the skill, so unrelated workshop items (mods without scripts,
blueprints, scenarios) stay out of the way.
"""

import os
import subprocess
import sys
import winreg
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "Data"
LOCAL_MODS_DIR = SCRIPT_DIR / "LocalMods"

CODE_INDEX_DIR = DATA_DIR / "CodeIndex"
MOD_LIST_FILE = DATA_DIR / "mods.json"
MOD_HASHES_FILE = DATA_DIR / "mod_hashes.json"

SE_APP_ID = "244850"


def _read_registry_install_location() -> str:
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App " + SE_APP_ID,
        ) as key:
            value, _ = winreg.QueryValueEx(key, "InstallLocation")
            return value
    except OSError:
        return ""


def resolve_workshop_path() -> Path:
    """Return the Steam Workshop content folder for Space Engineers."""
    game_root = os.environ.get("SE_GAME_ROOT", "").strip() or _read_registry_install_location()
    if not game_root:
        print(
            "ERROR: Could not detect Space Engineers install location.\n"
            "Please set the SE_GAME_ROOT environment variable to the game's root folder\n"
            "(the folder containing Bin64, Content, etc.).",
            file=sys.stderr,
        )
        sys.exit(1)
    steamapps = Path(game_root).resolve().parent.parent
    return steamapps / "workshop" / "content" / SE_APP_ID
