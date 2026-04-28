"""
Shared path resolution for the plugin skill.

All plugin data lives under the Data junction inside the skill folder. The
junction is created by Prepare.bat and points at %USERPROFILE%\\.se-dev\\plugin.
"""

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "Data"

PLUGIN_SOURCES_DIR = DATA_DIR / "Sources"
PLUGINHUB_DIR = DATA_DIR / "PluginHub"
PLUGINS_DIR = PLUGINHUB_DIR / "Plugins"
CODE_INDEX_DIR = DATA_DIR / "CodeIndex"
