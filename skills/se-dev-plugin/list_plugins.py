#!/usr/bin/env python3
"""
List Plugins from the configured registries (PluginHub + MagnetarHub)

Lists all available plugins from every configured registry, tagged by registry
and showing which ones have their source code downloaded locally.

Usage:
    python list_plugins.py [options]

Examples:
    python list_plugins.py                    # List all plugins
    python list_plugins.py --local            # List only locally available plugins
    python list_plugins.py --search "camera"  # Search plugins by name/description
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from plugin_paths import (
    MAGNETAR_PLUGINS_DIR,
    PLUGIN_SOURCES_DIR,
    PLUGINS_DIR,
    plugin_repo_ref,
    registry_plugin_dirs,
)


def _registry_label(plugins_dir: Path) -> str:
    if plugins_dir == PLUGINS_DIR:
        return "PluginHub"
    if plugins_dir == MAGNETAR_PLUGINS_DIR:
        return "MagnetarHub"
    return "custom"


def parse_plugin_xml(xml_file: Path) -> dict:
    """Parse a plugin XML file and extract relevant information."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        plugin_info = {
            "id": "",
            "repo": "",
            "name": "",
            "author": "",
            "tooltip": "",
            "description": "",
            "commit": "",
            "source_dirs": [],
            "hidden": False,
            "local": False,
            "registry": "",
            "xml_file": xml_file.name
        }

        # Extract fields
        id_elem = root.find("Id")
        if id_elem is not None and id_elem.text:
            plugin_info["id"] = id_elem.text.strip()

        # GitHub "Owner/Repo": <RepoId> (MagnetarHub) or <Id> (PluginHub).
        plugin_info["repo"] = plugin_repo_ref(root)

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
    """Load all plugins from every configured registry (PluginHub, MagnetarHub)."""
    registry_dirs = registry_plugin_dirs()
    if not registry_dirs:
        print("No plugin registry found.", file=sys.stderr)
        print("Run: uv run download_pluginhub.py  and/or  uv run download_magnetarhub.py",
              file=sys.stderr)
        return []

    plugins = []
    seen = set()
    for plugins_dir in registry_dirs:
        registry = _registry_label(plugins_dir)
        for xml_file in sorted(plugins_dir.glob("*.xml")):
            plugin = parse_plugin_xml(xml_file)
            if not plugin:
                continue
            key = (plugin["id"] or plugin["repo"] or plugin["xml_file"]).lower()
            if key in seen:
                continue
            seen.add(key)
            plugin["registry"] = registry
            plugin["local"] = False
            plugin["local_path"] = ""
            repo_ref = plugin.get("repo") or plugin["id"]
            if repo_ref:
                repo_name = repo_ref.split("/")[-1] if "/" in repo_ref else repo_ref
                local_path = PLUGIN_SOURCES_DIR / repo_name
                if local_path.exists():
                    plugin["local"] = True
                    plugin["local_path"] = str(local_path)
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
                   search_term in p["id"].lower() or
                   search_term in p.get("repo", "").lower()]

    # Output
    if args.json:
        import json
        print(json.dumps(plugins, indent=2))
    else:
        local_count = sum(1 for p in plugins if p["local"])
        print(f"Found {len(plugins)} plugins ({local_count} available locally)\n")

        for plugin in plugins:
            status = "[LOCAL]" if plugin["local"] else "[REMOTE]"
            registry = plugin.get("registry", "")
            reg_tag = f" [{registry}]" if registry else ""
            print(f"{status}{reg_tag} {plugin['name']}")
            print(f"  ID: {plugin['id']}")
            if plugin.get("repo") and plugin["repo"] != plugin["id"]:
                print(f"  Repo: {plugin['repo']}")
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
