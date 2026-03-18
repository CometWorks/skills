#!/usr/bin/env python3
"""
List Plugins from PluginHub

Lists all available plugins from the PluginHub registry, showing which ones
have their source code downloaded locally.

Usage:
    python list_plugins.py [options]

Examples:
    python list_plugins.py                    # List all plugins
    python list_plugins.py --local            # List only locally available plugins
    python list_plugins.py --search "camera"  # Search plugins by name/description
"""

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from plugin_paths import resolve_all_plugin_sources_dirs

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
            "author": "",
            "tooltip": "",
            "description": "",
            "commit": "",
            "source_dirs": [],
            "hidden": False,
            "local": False,
            "xml_file": xml_file.name
        }

        # Extract fields
        id_elem = root.find("Id")
        if id_elem is not None and id_elem.text:
            plugin_info["id"] = id_elem.text.strip()

        name_elem = root.find("FriendlyName")
        if name_elem is not None and name_elem.text:
            plugin_info["name"] = name_elem.text.strip()

        author_elem = root.find("Author")
        if author_elem is not None and author_elem.text:
            plugin_info["author"] = author_elem.text.strip()

        tooltip_elem = root.find("Tooltip")
        if tooltip_elem is not None and tooltip_elem.text:
            plugin_info["tooltip"] = tooltip_elem.text.strip()

        desc_elem = root.find("Description")
        if desc_elem is not None and desc_elem.text:
            plugin_info["description"] = desc_elem.text.strip()
        elif plugin_info["tooltip"]:
            plugin_info["description"] = plugin_info["tooltip"]

        commit_elem = root.find("Commit")
        if commit_elem is not None and commit_elem.text:
            plugin_info["commit"] = commit_elem.text.strip()

        source_dirs = root.find("SourceDirectories")
        if source_dirs is not None:
            for dir_elem in source_dirs.findall("Directory"):
                if dir_elem.text:
                    plugin_info["source_dirs"].append(dir_elem.text.strip())

        hidden_elem = root.find("Hidden")
        if hidden_elem is not None and hidden_elem.text:
            plugin_info["hidden"] = hidden_elem.text.strip().lower() == "true"

        return plugin_info
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}", file=sys.stderr)
        return None


def get_local_plugin_id(plugin_dir: Path) -> str:
    """Get plugin ID from a local plugin source directory."""
    # The directory name is typically the repo name (e.g., "ToolSwitcherPlugin")
    # We need to match it with the PluginHub ID format (e.g., "austinvaness/ToolSwitcherPlugin")
    return plugin_dir.name


def load_all_plugins() -> list:
    """Load all plugins from PluginHub."""
    if not PLUGINS_DIR.exists():
        print(f"PluginHub not found at {PLUGINHUB_DIR}", file=sys.stderr)
        print("Run: uv run download_pluginhub.py", file=sys.stderr)
        return []

    source_dirs = resolve_all_plugin_sources_dirs()

    plugins = []
    for xml_file in PLUGINS_DIR.glob("*.xml"):
        plugin = parse_plugin_xml(xml_file)
        if plugin:
            # Check if source is available locally in any source directory
            if plugin["id"]:
                repo_name = plugin["id"].split("/")[-1] if "/" in plugin["id"] else plugin["id"]
                plugin["local"] = False
                plugin["local_path"] = ""
                for src_dir in source_dirs:
                    local_path = src_dir / repo_name
                    if local_path.exists():
                        plugin["local"] = True
                        plugin["local_path"] = str(local_path)
                        break
            plugins.append(plugin)

    return sorted(plugins, key=lambda p: p["name"].lower())


def main():
    parser = argparse.ArgumentParser(description="List plugins from PluginHub")
    parser.add_argument("--local", action="store_true", help="Show only locally available plugins")
    parser.add_argument("--remote", action="store_true", help="Show only plugins not downloaded locally")
    parser.add_argument("--search", "-s", type=str, help="Search plugins by name or description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    args = parser.parse_args()

    plugins = load_all_plugins()

    if not plugins:
        sys.exit(1)

    # Apply filters
    if args.local:
        plugins = [p for p in plugins if p["local"]]
    elif args.remote:
        plugins = [p for p in plugins if not p["local"]]

    if args.search:
        search_term = args.search.lower()
        plugins = [p for p in plugins if
                   search_term in p["name"].lower() or
                   search_term in p["description"].lower() or
                   search_term in p["tooltip"].lower() or
                   search_term in p["id"].lower()]

    # Output
    if args.json:
        import json
        print(json.dumps(plugins, indent=2))
    else:
        local_count = sum(1 for p in plugins if p["local"])
        print(f"Found {len(plugins)} plugins ({local_count} available locally)\n")

        for plugin in plugins:
            status = "[LOCAL]" if plugin["local"] else "[REMOTE]"
            print(f"{status} {plugin['name']}")
            print(f"  ID: {plugin['id']}")
            print(f"  Author: {plugin['author']}")
            if args.verbose:
                if plugin["tooltip"]:
                    print(f"  Tooltip: {plugin['tooltip']}")
                if plugin["description"] and plugin["description"] != plugin["tooltip"]:
                    # Truncate long descriptions
                    desc = plugin["description"]
                    if len(desc) > 200:
                        desc = desc[:200] + "..."
                    print(f"  Description: {desc}")
                if plugin["local_path"]:
                    print(f"  Local path: {plugin['local_path']}")
            print()


if __name__ == "__main__":
    main()
