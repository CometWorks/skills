#!/usr/bin/env python3
"""
Quick inventory of installed mods.

Walks the Steam workshop folder and the local Mods folder, producing
Data/mods.json. This is the fast, frequently-refreshed index — it does NOT
parse C# code, so it is cheap to rerun before any task.

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

from mod_paths import (
    DATA_DIR,
    LOCAL_MODS_DIR,
    MOD_LIST_FILE,
    resolve_workshop_path,
)


def _scan_workshop(workshop_path: Path) -> list:
    if not workshop_path.exists():
        return []
    mods = []
    for item in workshop_path.iterdir():
        if not item.is_dir():
            continue
        scripts_dir = item / "Data" / "Scripts"
        cs_files = list(scripts_dir.rglob("*.cs")) if scripts_dir.exists() else []
        mods.append({
            "workshop_id": item.name,
            "name": item.name,
            "source": "steam",
            "path": str(item),
            "has_scripts": bool(cs_files),
            "script_count": len(cs_files),
        })
    return mods


def _scan_local(local_path: Path) -> list:
    if not local_path.exists():
        return []
    mods = []
    for item in local_path.iterdir():
        if not item.is_dir():
            continue
        cs_files = list(item.rglob("*.cs"))
        mods.append({
            "workshop_id": item.name,
            "name": item.name,
            "source": "local",
            "path": str(item),
            "has_scripts": bool(cs_files),
            "script_count": len(cs_files),
        })
    return mods


def build_inventory() -> list:
    workshop = resolve_workshop_path()
    return _scan_workshop(workshop) + _scan_local(LOCAL_MODS_DIR)


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    mods = build_inventory()
    with open(MOD_LIST_FILE, "w", encoding="utf-8") as f:
        json.dump({"mods": mods}, f, indent=2)

    steam_with_scripts = sum(1 for m in mods if m["source"] == "steam" and m["has_scripts"])
    local = sum(1 for m in mods if m["source"] == "local")
    print(f"Inventoried {len(mods)} mods "
          f"({steam_with_scripts} steam mods with scripts, {local} local).")
    print(f"Written to {MOD_LIST_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
