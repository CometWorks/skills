#!/usr/bin/env python3
"""Move ILSpyCmd output into case-collision-safe folders.

The Space Engineers .NET assemblies declare both ``X.Y.Gui`` and ``X.Y.GUI``
namespaces (and ``VRage.Filesystem`` vs ``VRage.FileSystem``). ILSpyCmd's
``--nested-directories`` mode writes one file per type into a folder path
that mirrors the namespace. On a case-sensitive filesystem (Linux) two
sibling folders are created (``Gui/`` and ``GUI/``); on a case-insensitive
filesystem (Windows, default macOS) the two map to the same physical
folder and ILSpyCmd silently commingles the files.

This script normalises the layout the same way on both platforms by
reading each ``.cs`` file's ``namespace`` declaration and moving files
whose namespace contains one of the upper-case variants into a sibling
folder with an explicit ``_UPPER`` suffix. The lower-case sibling is left
where ILSpyCmd produced it. The script is idempotent and may be re-run.

Usage:
    python fix_case_collisions.py <Data/Decompiled>
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

# C# namespace prefixes that collide with a same-spelled, differently-cased
# sibling on a case-insensitive filesystem. Each entry maps the namespace
# prefix as the compiler emits it to the disambiguated form used on disk.
NS_REWRITES: dict[str, str] = {
    "Sandbox.Game.GUI": "Sandbox.Game.GUI_UPPER",
    "Sandbox.Graphics.GUI": "Sandbox.Graphics.GUI_UPPER",
    "VRage.Game.GUI": "VRage.Game.GUI_UPPER",
    "VRage.FileSystem": "VRage.FileSystem_UPPER",
}

# Match ``namespace Foo.Bar.Baz`` followed by ``;`` (file-scoped) or ``{``.
NAMESPACE_RE = re.compile(
    r"^\s*namespace\s+([A-Za-z_][\w.]*)\s*[;{]", re.MULTILINE
)


def rewrite_namespace(ns: str) -> str | None:
    """Return the rewritten namespace, or ``None`` if no rewrite applies."""
    for old, new in NS_REWRITES.items():
        if ns == old:
            return new
        if ns.startswith(old + "."):
            return new + ns[len(old):]
    return None


def read_namespace(cs_path: Path) -> str | None:
    try:
        text = cs_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = NAMESPACE_RE.search(text)
    return m.group(1) if m else None


def fix_file(cs_path: Path, asm_root: Path) -> bool:
    """Move ``cs_path`` if its namespace requires a ``_UPPER`` folder.

    Returns True when a move was performed.
    """
    ns = read_namespace(cs_path)
    if ns is None:
        return False
    new_ns = rewrite_namespace(ns)
    if new_ns is None:
        return False
    target_dir = asm_root.joinpath(*new_ns.split("."))
    target = target_dir / cs_path.name
    # Same path (after case normalisation) -> nothing to do.
    try:
        if target.resolve() == cs_path.resolve():
            return False
    except OSError:
        pass
    target_dir.mkdir(parents=True, exist_ok=True)
    if target.exists():
        # Already moved by a previous run, or a duplicate produced by a
        # merged case-insensitive folder. If contents match, drop the
        # source; otherwise it's a situation we shouldn't paper over.
        if target.read_bytes() == cs_path.read_bytes():
            cs_path.unlink()
            return True
        raise SystemExit(
            f"ERROR: target {target} already exists with different "
            f"contents (source {cs_path})"
        )
    shutil.move(str(cs_path), str(target))
    return True


def find_case_collisions(asm_root: Path) -> list[tuple[Path, Path]]:
    """Return pairs of ``.cs`` files whose paths collide case-insensitively.

    Two paths under the same ``asm_root`` that map to the same
    case-folded string would resolve to the same physical file on a
    case-insensitive filesystem (Windows, default macOS). When ILSpyCmd
    runs on such a system, the second write silently overwrites the
    first and the type that lost the race is gone before this script
    ever sees the tree.

    On a case-sensitive filesystem (Linux) this function sees both
    siblings and reports the collision so the pipeline can fail loud
    instead of committing a tree that is broken on Windows. On a
    case-insensitive filesystem the OS has already merged the entries
    away, so this check trivially finds nothing - the loss can only be
    detected from the case-sensitive side.
    """
    by_lower: dict[str, Path] = {}
    collisions: list[tuple[Path, Path]] = []
    for root, _dirs, files in os.walk(asm_root):
        for fn in files:
            if not fn.endswith(".cs"):
                continue
            path = Path(root) / fn
            key = str(path.relative_to(asm_root)).lower()
            existing = by_lower.get(key)
            if existing is not None:
                collisions.append((existing, path))
            else:
                by_lower[key] = path
    return collisions


def fix_assembly(asm_root: Path) -> int:
    moved = 0
    for root, _dirs, files in os.walk(asm_root):
        for fn in files:
            if fn.endswith(".cs"):
                if fix_file(Path(root) / fn, asm_root):
                    moved += 1
    # Remove any directories that became empty after moves.
    for root, dirs, _files in os.walk(asm_root, topdown=False):
        for d in dirs:
            try:
                (Path(root) / d).rmdir()
            except OSError:
                pass
    return moved


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "Usage: fix_case_collisions.py <Data/Decompiled>",
            file=sys.stderr,
        )
        return 2
    decompiled = Path(argv[1]).resolve()
    if not decompiled.is_dir():
        print(f"ERROR: not a directory: {decompiled}", file=sys.stderr)
        return 2

    # Pre-flight: scan every assembly for case-insensitive path
    # collisions. Any collision means a future game version introduced
    # two types whose decompiled paths differ only in letter case, which
    # would silently lose data when ILSpyCmd writes them on Windows.
    # Aborting here on Linux prevents committing a tree that is broken
    # on the other platform.
    all_collisions: list[tuple[Path, Path]] = []
    for asm_dir in sorted(decompiled.iterdir()):
        if not asm_dir.is_dir():
            continue
        all_collisions.extend(find_case_collisions(asm_dir))
    if all_collisions:
        print(
            "ERROR: case-insensitive path collisions detected in the "
            "decompiled tree.",
            file=sys.stderr,
        )
        print(
            "These files would overwrite each other on Windows, where "
            "ILSpyCmd writes both to the same physical path:",
            file=sys.stderr,
        )
        for a, b in all_collisions:
            print(f"  {a}", file=sys.stderr)
            print(f"  {b}", file=sys.stderr)
        print(
            "A new case-variant namespace pair has likely been "
            "introduced. Investigate and either extend NS_REWRITES "
            "with a disambiguating suffix or change the decompile "
            "layout so the affected types do not share a folder.",
            file=sys.stderr,
        )
        return 3

    total = 0
    for asm_dir in sorted(decompiled.iterdir()):
        if not asm_dir.is_dir():
            continue
        n = fix_assembly(asm_dir)
        if n:
            print(f"  {asm_dir.name}: moved {n} file(s) into _UPPER folder(s)")
        total += n
    print(f"Done. Total files moved: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
