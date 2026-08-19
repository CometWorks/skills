#!/usr/bin/env python3
"""
Check whether the indexes under a CodeIndex directory are complete and usable.

Preparation rebuilds an index only when it is missing or broken, so an unchanged
decompilation is never re-indexed. This script is the single place that decides
what "complete" means, shared by Prepare.bat (Windows) and prepare.sh (Linux).

Modes:
    check_index.py <CodeIndex>
        Check the code index written by index_code.py.

    check_index.py --content <CodeIndex>
        Check the content index written by index_content.py.

Exit codes:
    0 = present and complete
    2 = missing or broken, the index has to be rebuilt
    1 = usage error
"""

import sys
from pathlib import Path


# Categories written as <name>_declarations.csv and <name>_usages.csv.
# Keep in sync with the `categories` list in index_code.py write_indices().
INDEX_CATEGORIES = (
    "namespace",
    "interface",
    "class",
    "struct",
    "enum",
    "method",
    "field",
    "property",
    "event",
    "constructor",
)

# Written by dedicated blocks of the same index_code.py function.
EXTRA_CODE_INDEX_FILES = (
    "delegate_declarations.csv",
    "enum_member_declarations.csv",
    "method_signatures.csv",
    "class_hierarchy.csv",
    "interface_hierarchy.csv",
    "interface_implementation.csv",
)

# class_hierarchy.txt and interface_hierarchy.txt are written only when the
# corresponding hierarchy has entries, so they are not required here.

CONTENT_INDEX_FILES = ("content_index.csv",)


def code_index_files():
    names = []
    for category in INDEX_CATEGORIES:
        names.append(f"{category}_declarations.csv")
        names.append(f"{category}_usages.csv")
    names.extend(EXTRA_CODE_INDEX_FILES)
    return tuple(names)


def defect(path: Path) -> str:
    """Empty string if the index file looks usable, otherwise the defect."""
    if not path.is_file():
        return "is missing"
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            header = f.readline()
    except OSError as e:
        return f"is unreadable ({e})"
    # An interrupted write leaves a zero length or truncated file behind. Every
    # index file starts with a multi column CSV header row.
    if not header.strip():
        return "is empty"
    if "," not in header:
        return "has no CSV header row"
    return ""


def check(index_dir: Path, names, label: str) -> int:
    if not index_dir.is_dir():
        print(f"MISSING: no {label} directory at {index_dir}")
        return 2

    for name in names:
        problem = defect(index_dir / name)
        if problem:
            print(f"BROKEN: {label} file {name} {problem}")
            return 2

    print(f"OK: all {len(names)} {label} files present at {index_dir}")
    return 0


def main(argv):
    args = list(argv[1:])
    content = False
    if args and args[0] == "--content":
        content = True
        args.pop(0)

    if len(args) != 1:
        print("Usage: check_index.py [--content] <CodeIndex>", file=sys.stderr)
        return 1

    index_dir = Path(args[0])
    if content:
        return check(index_dir, CONTENT_INDEX_FILES, "content index")
    return check(index_dir, code_index_files(), "code index")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
