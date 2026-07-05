"""
Shared path resolution for the plugin skill.

All plugin data lives under the Data symlink/junction inside the skill folder.
The link is created by Prepare.bat / prepare.sh and points at the per-user
persistent skill data directory.

Two plugin registries are supported and searched together:
  - PluginHub   (client plugins, loaded by Pulsar)   -> Data/PluginHub/Plugins
  - MagnetarHub (server plugins, loaded by Magnetar)  -> Data/MagnetarHub/Plugins

Both use the same GitHubPlugin XML schema. PluginHub puts "Owner/Repo" in <Id>;
MagnetarHub puts a GUID in <Id> and the "Owner/Repo" in <RepoId>. Use
plugin_repo_ref() to get the clone reference regardless of which registry an
entry came from.
"""

import os
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "Data"

PLUGIN_SOURCES_DIR = DATA_DIR / "Sources"

PLUGINHUB_DIR = DATA_DIR / "PluginHub"
PLUGINS_DIR = PLUGINHUB_DIR / "Plugins"

MAGNETARHUB_DIR = DATA_DIR / "MagnetarHub"
MAGNETAR_PLUGINS_DIR = MAGNETARHUB_DIR / "Plugins"

CODE_INDEX_DIR = DATA_DIR / "CodeIndex"
PLUGIN_LIST_FILE = DATA_DIR / "plugins.json"


def registry_plugin_dirs(existing_only: bool = True):
    """Ordered list of registry 'Plugins' directories to search.

    Order: an optional extra registry from the SE_PLUGIN_REGISTRY_DIR
    environment variable (point it at a registry root containing a 'Plugins'
    subfolder, or directly at a folder of *.xml files), then the cloned
    PluginHub and MagnetarHub registries. Duplicates are removed. When
    existing_only is True (default) only directories that exist are returned.
    """
    dirs = []

    override = os.environ.get("SE_PLUGIN_REGISTRY_DIR", "").strip()
    if override:
        root = Path(override).expanduser()
        nested = root / "Plugins"
        dirs.append(nested if nested.is_dir() else root)

    dirs.append(PLUGINS_DIR)
    dirs.append(MAGNETAR_PLUGINS_DIR)

    seen = set()
    result = []
    for d in dirs:
        key = str(d)
        if key in seen:
            continue
        seen.add(key)
        if existing_only and not d.is_dir():
            continue
        result.append(d)
    return result


def iter_registry_xml():
    """Yield every plugin XML file across all registry directories."""
    for plugins_dir in registry_plugin_dirs():
        yield from sorted(plugins_dir.glob("*.xml"))


def plugin_repo_ref(root: ET.Element) -> str:
    """Return the GitHub 'Owner/Repo' reference for a plugin XML root element.

    Prefers <RepoId> (MagnetarHub style, where <Id> is a GUID) and falls back
    to <Id> (PluginHub style, where <Id> itself is 'Owner/Repo'). Returns an
    empty string when neither is present.
    """
    for tag in ("RepoId", "Id"):
        elem = root.find(tag)
        if elem is not None and elem.text and elem.text.strip():
            if tag == "RepoId" or "/" in elem.text.strip():
                return elem.text.strip()
    # Fall back to raw <Id> even if it is not Owner/Repo, so callers can report
    # a meaningful "invalid reference" error rather than an empty one.
    id_elem = root.find("Id")
    if id_elem is not None and id_elem.text:
        return id_elem.text.strip()
    return ""
