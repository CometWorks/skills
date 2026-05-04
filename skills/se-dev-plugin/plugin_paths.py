"""
Shared path resolution for the plugin skill.

All plugin data lives under the Data symlink/junction inside the skill folder.
The link is created by Prepare.bat / Prepare.sh and points at the per-user
persistent skill data directory.
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "Data"

PLUGIN_SOURCES_DIR = DATA_DIR / "Sources"
PLUGINHUB_DIR = DATA_DIR / "PluginHub"
PLUGINS_DIR = PLUGINHUB_DIR / "Plugins"
CODE_INDEX_DIR = DATA_DIR / "CodeIndex"
PLUGIN_LIST_FILE = DATA_DIR / "plugins.json"
