"""
Shared path helpers for the mod skill.

All persistent mod data lives under the Data symlink/junction inside the skill
folder. The link is created by Prepare.bat / Prepare.sh and points at the
per-user persistent skill data directory.

Steam workshop content is read directly from its Steam folder rather than
symlinked into the skill, so unrelated workshop items (mods without scripts,
blueprints, scenarios) stay out of the way.
"""

import os
import subprocess
import sys
from pathlib import Path

try:
    import winreg
except ImportError:
    winreg = None

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "Data"
LOCAL_MODS_DIR = SCRIPT_DIR / "LocalMods"

CODE_INDEX_DIR = DATA_DIR / "CodeIndex"
MOD_LIST_FILE = DATA_DIR / "mods.json"
MOD_HASHES_FILE = DATA_DIR / "mod_hashes.json"

SE_APP_ID = "244850"


def _read_registry_install_location() -> str:
    if winreg is None:
        return ""
    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App " + SE_APP_ID,
        ) as key:
            value, _ = winreg.QueryValueEx(key, "InstallLocation")
            return value
    except OSError:
        return ""


def _steamapps_candidates():
    steamapps_dir = os.environ.get("STEAMAPPS_DIR", "").strip()
    if steamapps_dir:
        yield Path(steamapps_dir).expanduser()

    home = Path.home()
    for candidate in (
        home / ".local/share/Steam/steamapps",
        home / ".steam/steam/steamapps",
        home / ".steam/root/steamapps",
        home / ".steam/debian-installation/steamapps",
        home / ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps",
        home / "Library/Application Support/Steam/steamapps",
    ):
        yield candidate


def _resolve_game_root() -> Path | None:
    env_root = os.environ.get("SE_GAME_ROOT", "").strip()
    if env_root:
        return Path(env_root).expanduser()

    registry_root = _read_registry_install_location()
    if registry_root:
        return Path(registry_root)

    for steamapps in _steamapps_candidates():
        candidate = steamapps / "common" / "SpaceEngineers"
        if candidate.is_dir():
            return candidate
    return None


def resolve_workshop_path() -> Path:
    """Return the Steam Workshop content folder for Space Engineers."""
    game_root = _resolve_game_root()
    if game_root is None:
        print(
            "ERROR: Could not detect Space Engineers install location.\n"
            "Please set the SE_GAME_ROOT environment variable to the game's root folder\n"
            "(the folder containing Bin64, Content, etc.).",
            file=sys.stderr,
        )
        sys.exit(1)
    steamapps = game_root.resolve().parent.parent
    return steamapps / "workshop" / "content" / SE_APP_ID
