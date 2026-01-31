#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
INDEX_DIR = SCRIPT_DIR / "CodeIndex"

CATEGORY_FILES = {
    "class": ("class_declarations.csv", "class_usages.csv"),
    "method": ("method_declarations.csv", "method_usages.csv"),
    "enum": ("enum_declarations.csv", "enum_usages.csv"),
    "struct": ("struct_declarations.csv", "struct_usages.csv"),
    "interface": ("interface_declarations.csv", "interface_usages.csv"),
    "field": ("field_declarations.csv", "field_usages.csv"),
    "signature": ("method_signatures.csv", None),  # Signatures are declarations only
}

def parse_args():
    parser = argparse.ArgumentParser(description="Search C# code index")
    parser.add_argument("-c", "--count", action="store_true", help="Print only the count of matches")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limit number of results")
    parser.add_argument("-o", "--offset", type=int, default=0, help="Skip first N results")
    parser.add_argument("-n", "--namespace", type=str, default="", help="Filter by namespace prefix")
    parser.add_argument("category", choices=CATEGORY_FILES.keys(), help="Symbol category")
    parser.add_argument("symbol_type", choices=["declaration", "usage"], help="Symbol type")
    parser.add_argument("patterns", nargs="+", help="Search patterns (text:X or re:X)")
    return parser.parse_args()

def compile_pattern(pattern_str):
    if pattern_str.startswith("re:"):
        return ("regex", re.compile(pattern_str[3:], re.IGNORECASE))
    elif pattern_str.startswith("text:"):
        return ("text", pattern_str[5:].lower())
    else:
        return ("text", pattern_str.lower())

def get_symbol_name(row, category):
    if category == "method":
        return row["method"]
    elif category == "field":
        return row["symbol_name"]
    elif category == "signature":
        return row["method_name"]
    else:
        return row["declaring_type"]

def matches_pattern(name, pattern):
    mode, value = pattern
    if mode == "regex":
        return value.search(name) is not None
    else:
        return value in name.lower()

def get_depth(row, category):
    depth = 0
    if row["namespace"]:
        depth += row["namespace"].count(".") + 1
    if row["declaring_type"]:
        depth += 1
    # Handle different column name for signature category
    method_col = "method_name" if category == "signature" else "method"
    if row.get(method_col):
        depth += 1
    return depth

def get_sort_key(row, category):
    # Handle different column names for signature category
    method_col = "method_name" if category == "signature" else "method"
    symbol_col = "signature" if category == "signature" else "symbol_name"
    return (
        get_depth(row, category),
        row["namespace"],
        row["declaring_type"],
        row.get(method_col, ""),
        row.get(symbol_col, ""),
        row["file_path"],
        int(row["start_line"]),
    )

def main():
    args = parse_args()

    # Select the appropriate file based on symbol_type (declaration or usage)
    decl_file, usage_file = CATEGORY_FILES[args.category]

    # Signature category only has declarations
    if args.category == "signature" and args.symbol_type == "usage":
        print("NO-MATCHES")
        sys.exit(0)

    if args.symbol_type == "declaration":
        index_file = INDEX_DIR / decl_file
    else:
        if usage_file is None:
            print("NO-MATCHES")
            sys.exit(0)
        index_file = INDEX_DIR / usage_file

    if not index_file.exists():
        print("NO-MATCHES")
        sys.exit(0)

    patterns = [compile_pattern(p) for p in args.patterns]
    ns_filter = args.namespace.lower() if args.namespace else ""

    matches = []
    with open(index_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if ns_filter:
                row_ns = row["namespace"].lower()
                if not (row_ns == ns_filter or row_ns.startswith(ns_filter + ".")):
                    continue
            name = get_symbol_name(row, args.category)
            if all(matches_pattern(name, p) for p in patterns):
                matches.append(row)

    if not matches:
        print("NO-MATCHES")
        sys.exit(0)

    if args.count:
        print(len(matches))
        sys.exit(0)

    matches.sort(key=lambda row: get_sort_key(row, args.category))

    if args.offset > 0:
        matches = matches[args.offset:]
    if args.limit > 0:
        matches = matches[:args.limit]

    for row in matches:
        start = row["start_line"]
        end = row["end_line"]
        if start == end:
            location = f"{row['file_path']}:{start}"
        else:
            location = f"{row['file_path']}:{start}-{end}"

        if args.category == "signature":
            # For signatures, append the signature text after a pipe separator
            print(f"{location}|{row['signature']}")
        else:
            print(location)

if __name__ == "__main__":
    main()
