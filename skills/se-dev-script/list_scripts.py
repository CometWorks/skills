#!/usr/bin/env python3
"""
Quick inventory of installed PB scripts.

Walks the Steam workshop folder and the local IngameScripts folder, producing
Data/scripts.json. This is the fast, frequently-refreshed index — it does NOT
parse C# code, so it is cheap to rerun before any task.

A Steam workshop entry counts as a PB script if it contains a top-level
`Script.cs` file (the standard PB script layout). Other workshop content
types (mods, blueprints, scenarios) are skipped.

Output entries:
    {
        "workshop_id": "<numeric folder name, or repo dir name for local>",
        "name": "<workshop_id or local folder name>",
        "source": "steam" | "local",
        "path": "<absolute path>",
        "has_scripts": true | false,
        "script_count": <number of .cs files>
    }
"""

import json
import sys
from pathlib import Path

from script_paths import (
    DATA_DIR,
    LOCAL_SCRIPTS_DIR,
    SCRIPT_LIST_FILE,
    resolve_workshop_path,
)


def _scan_workshop(workshop_path: Path) -> list:
    if not workshop_path.exists():
        return []
    scripts = []
    for item in workshop_path.iterdir():
        if not item.is_dir():
            continue
        # PB scripts have a top-level Script.cs file. Without it, this is a
        # mod, blueprint, scenario, or something else — skip it.
        if not (item / "Script.cs").exists():
            continue
        cs_files = list(item.rglob("*.cs"))
        scripts.append({
            "workshop_id": item.name,
            "name": item.name,
            "source": "steam",
            "path": str(item),
            "has_scripts": bool(cs_files),
            "script_count": len(cs_files),
        })
    return scripts


def _scan_local(local_path: Path) -> list:
    if not local_path.exists():
        return []
    scripts = []
    for item in local_path.iterdir():
        if not item.is_dir():
            continue
        cs_files = list(item.rglob("*.cs"))
        if not cs_files:
            continue
        scripts.append({
            "workshop_id": item.name,
            "name": item.name,
            "source": "local",
            "path": str(item),
            "has_scripts": True,
            "script_count": len(cs_files),
        })
    return scripts


def build_inventory() -> list:
    workshop = resolve_workshop_path()
    return _scan_workshop(workshop) + _scan_local(LOCAL_SCRIPTS_DIR)


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    scripts = build_inventory()
    with open(SCRIPT_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump({"scripts": scripts}, f, indent=2)

    steam = sum(1 for s in scripts if s["source"] == "steam")
    local = sum(1 for s in scripts if s["source"] == "local")
    print(f"Inventoried {len(scripts)} PB scripts ({steam} steam, {local} local).")
    print(f"Written to {SCRIPT_LIST_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
