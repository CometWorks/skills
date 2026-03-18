"""
Shared path resolution for plugin source downloads.

Both download_plugin_source.py and index_plugins.py use this module to
determine where plugin sources are stored.
"""

import os
import platform
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()


def _read_config_from_file(file_path: Path) -> str:
    """Read plugin_download_folder or PLUGIN_DOWNLOAD_FOLDER from a config file."""
    if not file_path.exists():
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Match: plugin_download_folder: /path/to/folder
                m = re.match(r"plugin_download_folder:\s*(.+)", line, re.IGNORECASE)
                if m:
                    return m.group(1).strip()
                # Match: PLUGIN_DOWNLOAD_FOLDER=/path/to/folder
                m = re.match(r"PLUGIN_DOWNLOAD_FOLDER=(.+)", line)
                if m:
                    return m.group(1).strip()
    except Exception:
        pass
    return ""


def resolve_plugin_sources_dir() -> Path:
    """
    Resolve the plugin sources directory using this priority:

    1. Environment variable SE_PLUGIN_DOWNLOAD_FOLDER
    2. CLAUDE.md or AGENTS.md in the current working directory
    3. OS-specific temp folder (default)

    Returns the resolved Path.
    """
    # 1. Environment variable
    env_folder = os.environ.get("SE_PLUGIN_DOWNLOAD_FOLDER", "").strip()
    if env_folder:
        return Path(env_folder)

    # 2. Check CLAUDE.md and AGENTS.md in CWD
    cwd = Path.cwd()
    for config_name in ("CLAUDE.md", "AGENTS.md"):
        config_path = cwd / config_name
        folder = _read_config_from_file(config_path)
        if folder:
            return Path(folder)

    # 3. OS-specific temp folder
    if platform.system() == "Windows":
        temp_base = os.environ.get("TEMP", os.environ.get("TMP", ""))
        if temp_base:
            return Path(temp_base) / "se-dev-plugin" / "plugins"
        # Fallback for Windows without TEMP
        return Path(os.path.expanduser("~")) / "AppData" / "Local" / "Temp" / "se-dev-plugin" / "plugins"
    else:
        # Linux / macOS
        return Path("/tmp") / "se-dev-plugin" / "plugins"


def resolve_all_plugin_sources_dirs() -> list:
    """
    Return all directories that may contain plugin sources.

    Used by the indexer to find sources from both the download location
    and the skill-local PluginSources/ directory (populated during preparation).

    Returns a list of existing Paths.
    """
    dirs = []
    # Primary: the configured/temp download directory
    download_dir = resolve_plugin_sources_dir()
    if download_dir.exists():
        dirs.append(download_dir)
    # Secondary: skill-local PluginSources/ (from preparation)
    local_dir = SCRIPT_DIR / "PluginSources"
    if local_dir.exists() and local_dir != download_dir:
        dirs.append(local_dir)
    return dirs


def ensure_plugin_sources_dir() -> Path:
    """
    Resolve and create the plugin sources directory.
    Raises an error with a helpful message if creation fails.
    """
    plugin_dir = resolve_plugin_sources_dir()
    try:
        plugin_dir.mkdir(parents=True, exist_ok=True)
        return plugin_dir
    except OSError as e:
        print(
            f"ERROR: Cannot create plugin download folder: {plugin_dir}\n"
            f"  Reason: {e}\n"
            f"\n"
            f"Please specify a writable plugin download folder by one of:\n"
            f"  1. Set environment variable: SE_PLUGIN_DOWNLOAD_FOLDER=/path/to/folder\n"
            f"  2. Add to CLAUDE.md or AGENTS.md in your project directory:\n"
            f"     plugin_download_folder: /path/to/folder\n",
            file=sys.stderr,
        )
        sys.exit(1)
