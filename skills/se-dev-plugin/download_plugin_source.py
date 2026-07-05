#!/usr/bin/env python3
"""
Clone Plugin Source Code from GitHub

Clones the source code of a plugin from its GitHub repository into the skill's
profile folder at Data/Sources/<RepoName>/. Cloning (rather than zip download)
keeps each plugin source updatable via git pull.

Usage:
    python download_plugin_source.py <plugin_id_or_name>

Examples:
    python download_plugin_source.py austinvaness/ToolSwitcherPlugin
    python download_plugin_source.py "Tool Switcher"
    python download_plugin_source.py ToolSwitcherPlugin
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from plugin_paths import (
    PLUGIN_SOURCES_DIR,
    SCRIPT_DIR,
    iter_registry_xml,
    plugin_repo_ref,
    registry_plugin_dirs,
)


def parse_plugin_xml(xml_file: Path) -> dict:
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        plugin_info = {
            "id": "",
            "repo": "",
            "name": "",
            "commit": "",
            "source_dirs": [],
        }

        id_elem = root.find("Id")
        if id_elem is not None and id_elem.text:
            plugin_info["id"] = id_elem.text.strip()

        # The GitHub "Owner/Repo" reference comes from <RepoId> (MagnetarHub
        # style, where <Id> is a GUID) and falls back to <Id> (PluginHub style,
        # where <Id> itself is "Owner/Repo").
        plugin_info["repo"] = plugin_repo_ref(root)

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
    if not registry_plugin_dirs():
        print("No plugin registry found.", file=sys.stderr)
        print("Run: uv run download_pluginhub.py  and/or  uv run download_magnetarhub.py",
              file=sys.stderr)
        return None

    search_lower = search_term.lower()
    matches = []

    for xml_file in iter_registry_xml():
        plugin = parse_plugin_xml(xml_file)
        if plugin:
            if plugin["id"].lower() == search_lower:
                return plugin
            if plugin["repo"].lower() == search_lower:
                return plugin
            if plugin["name"].lower() == search_lower:
                return plugin
            repo_name = plugin["repo"].split("/")[-1] if "/" in plugin["repo"] else plugin["repo"]
            if repo_name.lower() == search_lower:
                return plugin
            if (search_lower in plugin["id"].lower() or
                search_lower in plugin["repo"].lower() or
                search_lower in plugin["name"].lower() or
                search_lower in repo_name.lower()):
                matches.append(plugin)

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Multiple plugins match '{search_term}':")
        for m in matches:
            print(f"  - {m['name']} ({m['id']})")
        print("\nPlease specify the exact plugin ID.")
        return None
    print(f"No plugin found matching '{search_term}'")
    return None


def _run_git(args: list, cwd=None) -> int:
    return subprocess.run(["git", *args], cwd=cwd).returncode


def clone_plugin(plugin: dict) -> bool:
    repo_ref = plugin.get("repo") or plugin.get("id", "")
    if "/" not in repo_ref:
        print(
            f"Invalid repository reference '{repo_ref}': expected GitHub Owner/Repo style "
            f"(from <RepoId>, or <Id> as a fallback).",
            file=sys.stderr,
        )
        return False

    PLUGIN_SOURCES_DIR.mkdir(parents=True, exist_ok=True)

    owner, repo = repo_ref.split("/", 1)
    commit = plugin.get("commit", "").strip()
    repo_url = f"https://github.com/{owner}/{repo}.git"
    dest_dir = PLUGIN_SOURCES_DIR / repo

    if (dest_dir / ".git").exists():
        print(f"Updating existing clone at {dest_dir}")
        if _run_git(["fetch", "--tags", "--prune"], cwd=dest_dir) != 0:
            return False
        if commit:
            if _run_git(["checkout", "--detach", commit], cwd=dest_dir) != 0:
                return False
        else:
            if _run_git(["pull", "--ff-only"], cwd=dest_dir) != 0:
                return False
    else:
        if dest_dir.exists():
            print(f"ERROR: {dest_dir} exists but is not a git clone. Remove it manually.",
                  file=sys.stderr)
            return False
        print(f"Cloning {plugin['name']} from {repo_url} into {dest_dir}")
        if _run_git(["clone", repo_url, str(dest_dir)]) != 0:
            return False
        if commit:
            if _run_git(["checkout", "--detach", commit], cwd=dest_dir) != 0:
                return False

    print("\nIndexing plugin code...")
    index_script = SCRIPT_DIR / "index_plugins.py"
    result = subprocess.run(["uv", "run", str(index_script)], cwd=SCRIPT_DIR)
    if result.returncode != 0:
        print("Warning: Indexing failed", file=sys.stderr)
        return False

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
        sys.exit(0 if clone_plugin(plugin) else 1)
    sys.exit(1)


if __name__ == "__main__":
    main()
