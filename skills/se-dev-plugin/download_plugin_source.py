#!/usr/bin/env python3
"""
Download Plugin Source Code from GitHub

Downloads the source code of a plugin from its GitHub repository.

The download folder is determined by (in priority order):
1. SE_PLUGIN_DOWNLOAD_FOLDER environment variable
2. plugin_download_folder setting in CLAUDE.md or AGENTS.md (in CWD)
3. OS-specific temp folder: %TEMP%/se-dev-plugin/plugins/ (Windows)
   or /tmp/se-dev-plugin/plugins/ (Linux)

Usage:
    python download_plugin_source.py <plugin_id_or_name>

Examples:
    python download_plugin_source.py austinvaness/ToolSwitcherPlugin
    python download_plugin_source.py "Tool Switcher"
    python download_plugin_source.py ToolSwitcherPlugin
"""

import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import requests

from plugin_paths import ensure_plugin_sources_dir

SCRIPT_DIR = Path(__file__).parent.resolve()
PLUGINHUB_DIR = SCRIPT_DIR / "PluginHub"
PLUGINS_DIR = PLUGINHUB_DIR / "Plugins"


def parse_plugin_xml(xml_file: Path) -> dict:
    """Parse a plugin XML file and extract relevant information."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        plugin_info = {
            "id": "",
            "name": "",
            "commit": "",
            "source_dirs": [],
        }

        id_elem = root.find("Id")
        if id_elem is not None and id_elem.text:
            plugin_info["id"] = id_elem.text.strip()

        name_elem = root.find("FriendlyName")
        if name_elem is not None and name_elem.text:
            plugin_info["name"] = name_elem.text.strip()

        commit_elem = root.find("Commit")
        if commit_elem is not None and commit_elem.text:
            plugin_info["commit"] = commit_elem.text.strip()

        source_dirs = root.find("SourceDirectories")
        if source_dirs is not None:
            for dir_elem in source_dirs.findall("Directory"):
                if dir_elem.text:
                    plugin_info["source_dirs"].append(dir_elem.text.strip())

        return plugin_info
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}", file=sys.stderr)
        return None


def find_plugin(search_term: str) -> dict:
    """Find a plugin by ID, name, or partial match."""
    if not PLUGINS_DIR.exists():
        print(f"PluginHub not found at {PLUGINHUB_DIR}", file=sys.stderr)
        print("Run: uv run download_pluginhub.py", file=sys.stderr)
        return None

    search_lower = search_term.lower()
    matches = []

    for xml_file in PLUGINS_DIR.glob("*.xml"):
        plugin = parse_plugin_xml(xml_file)
        if plugin:
            # Exact ID match
            if plugin["id"].lower() == search_lower:
                return plugin

            # Exact name match
            if plugin["name"].lower() == search_lower:
                return plugin

            # Repo name match (e.g., "ToolSwitcherPlugin" matches "austinvaness/ToolSwitcherPlugin")
            repo_name = plugin["id"].split("/")[-1] if "/" in plugin["id"] else plugin["id"]
            if repo_name.lower() == search_lower:
                return plugin

            # Partial matches
            if (search_lower in plugin["id"].lower() or
                search_lower in plugin["name"].lower() or
                search_lower in repo_name.lower()):
                matches.append(plugin)

    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"Multiple plugins match '{search_term}':")
        for m in matches:
            print(f"  - {m['name']} ({m['id']})")
        print("\nPlease specify the exact plugin ID.")
        return None
    else:
        print(f"No plugin found matching '{search_term}'")
        return None


def download_plugin(plugin: dict) -> bool:
    """Download a plugin's source code from GitHub."""
    if not plugin["id"]:
        print("Plugin has no GitHub ID", file=sys.stderr)
        return False

    # Resolve and create the plugin sources directory
    plugin_sources_dir = ensure_plugin_sources_dir()
    print(f"Plugin sources directory: {plugin_sources_dir}")

    # Extract repo info
    parts = plugin["id"].split("/")
    if len(parts) != 2:
        print(f"Invalid plugin ID format: {plugin['id']}", file=sys.stderr)
        return False

    owner, repo = parts
    commit = plugin.get("commit", "main")

    # Destination directory
    dest_dir = plugin_sources_dir / repo

    # If already exists, remove it for fresh download
    if dest_dir.exists():
        print(f"Removing existing directory: {dest_dir}")
        shutil.rmtree(dest_dir)

    # Download ZIP from GitHub
    if commit:
        zip_url = f"https://github.com/{owner}/{repo}/archive/{commit}.zip"
    else:
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"

    print(f"Downloading {plugin['name']} from GitHub...")
    print(f"  URL: {zip_url}")

    try:
        response = requests.get(zip_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to download: {e}", file=sys.stderr)
        return False

    # Save and extract ZIP
    zip_path = plugin_sources_dir / "temp_download.zip"
    with open(zip_path, 'wb') as f:
        f.write(response.content)

    print("Extracting...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(plugin_sources_dir)
    except zipfile.BadZipFile as e:
        print(f"Failed to extract: {e}", file=sys.stderr)
        zip_path.unlink()
        return False

    # Rename extracted directory (GitHub adds commit hash to folder name)
    for item in plugin_sources_dir.iterdir():
        if item.is_dir() and item.name.startswith(repo):
            item.rename(dest_dir)
            break

    # Clean up
    zip_path.unlink()

    print(f"Downloaded to: {dest_dir}")

    # Run indexing
    print("\nIndexing plugin code...")
    index_script = SCRIPT_DIR / "index_plugins.py"
    result = subprocess.run(["uv", "run", str(index_script)], cwd=SCRIPT_DIR)
    if result.returncode != 0:
        print("Warning: Indexing failed", file=sys.stderr)

    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python download_plugin_source.py <plugin_id_or_name>")
        print("\nExamples:")
        print("  python download_plugin_source.py austinvaness/ToolSwitcherPlugin")
        print("  python download_plugin_source.py \"Tool Switcher\"")
        print("  python download_plugin_source.py ToolSwitcherPlugin")
        print("\nTo list available plugins, run: uv run list_plugins.py")
        sys.exit(1)

    search_term = " ".join(sys.argv[1:])
    plugin = find_plugin(search_term)

    if plugin:
        success = download_plugin(plugin)
        sys.exit(0 if success else 1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
