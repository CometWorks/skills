#!/usr/bin/env python3
"""
Mod Code Search Tool

Search the mod code index for classes, methods, fields, interfaces, etc.

Usage:
    python search_mods.py <category> <symbol_type> <pattern> [options]

Examples:
    python search_mods.py class declaration MyBlock
    python search_mods.py method usage Update
    python search_mods.py class children MyBaseClass
"""

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
INDEX_DIR = SCRIPT_DIR / "ModCodeIndex"

CATEGORY_FILES = {
    "class": ("class_declarations.csv", "class_usages.csv"),
    "method": ("method_declarations.csv", "method_usages.csv"),
    "enum": ("enum_declarations.csv", "enum_usages.csv"),
    "struct": ("struct_declarations.csv", "struct_usages.csv"),
    "interface": ("interface_declarations.csv", "interface_usages.csv"),
    "field": ("field_declarations.csv", "field_usages.csv"),
    "property": ("property_declarations.csv", "property_usages.csv"),
    "event": ("event_declarations.csv", "event_usages.csv"),
    "constructor": ("constructor_declarations.csv", "constructor_usages.csv"),
    "namespace": ("namespace_declarations.csv", "namespace_usages.csv"),
}

HIERARCHY_SUBCOMMANDS = {"parent", "children", "implements", "implementors"}
METHOD_SUBCOMMANDS = {"signature"}


def parse_args():
    parser = argparse.ArgumentParser(description="Search mod code index")
    parser.add_argument("-c", "--count", action="store_true", help="Print only the count of matches")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limit number of results")
    parser.add_argument("-o", "--offset", type=int, default=0, help="Skip first N results")
    parser.add_argument("-n", "--namespace", type=str, default="", help="Filter by namespace prefix")
    parser.add_argument("-i", "--case-insensitive", action="store_true", help="Make pattern matching case-insensitive")
    parser.add_argument("category", choices=list(CATEGORY_FILES.keys()), help="Symbol category")
    parser.add_argument("symbol_type", help="Symbol type (declaration/usage), method subcommand (signature), or hierarchy subcommand (parent/children/implements/implementors)")
    parser.add_argument("patterns", nargs="+", help="Search patterns (text:X or re:X)")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    return parser.parse_args()


def compile_pattern(pattern_str, case_insensitive=False):
    if pattern_str.startswith("re:"):
        flags = re.IGNORECASE if case_insensitive else 0
        return ("regex", re.compile(pattern_str[3:], flags))
    elif pattern_str.startswith("text:"):
        text = pattern_str[5:]
        return ("text", text.lower() if case_insensitive else text, case_insensitive)
    else:
        return ("text", pattern_str.lower() if case_insensitive else pattern_str, case_insensitive)


def is_mangled_name(name):
    """Check if a class name contains mangled/encoded characters."""
    return "_003C" in name


def strip_mangled_generics(name):
    """Extract the meaningful class name from a potentially mangled class name."""
    idx = name.find("_003C")
    if idx > 0:
        return name[:idx]
    return name


def get_symbol_name(row, is_signature=False, strip_generics=False):
    if is_signature:
        return row["method_name"]
    elif "method" in row and row["method"]:
        return row["method"]
    elif "symbol_name" in row and row["symbol_name"]:
        return row["symbol_name"]
    elif "declaring_type" in row and row["declaring_type"]:
        name = row["declaring_type"]
        if strip_generics:
            name = strip_mangled_generics(name)
        return name
    else:
        return row.get("namespace", "")


def matches_pattern(name, pattern):
    if pattern[0] == "regex":
        regex_obj = pattern[1]
        return regex_obj.search(name) is not None
    else:
        _, search_text, case_insensitive = pattern
        if case_insensitive:
            return search_text in name.lower()
        else:
            return search_text in name


def matches_pattern_prefix(name, pattern):
    """Match pattern at the start of name only."""
    if pattern[0] == "regex":
        regex_obj = pattern[1]
        match = regex_obj.search(name)
        return match is not None and match.start() == 0
    else:
        _, search_text, case_insensitive = pattern
        if case_insensitive:
            return name.lower().startswith(search_text)
        else:
            return name.startswith(search_text)


def get_depth(row, is_signature=False):
    depth = 0
    if row["namespace"]:
        depth += row["namespace"].count(".") + 1
    if row["declaring_type"]:
        depth += 1
    method_col = "method_name" if is_signature else "method"
    if row.get(method_col):
        depth += 1
    return depth


def get_sort_key(row, is_signature=False):
    method_col = "method_name" if is_signature else "method"
    symbol_col = "signature" if is_signature else "symbol_name"
    return (
        get_depth(row, is_signature),
        row["namespace"],
        row["declaring_type"],
        row.get(method_col, ""),
        row.get(symbol_col, ""),
        row["file_path"],
        int(row["start_line"]),
    )


def search_hierarchy_parent(category, patterns, ns_filter):
    """Search for parent class/interface of matching types"""
    if category == "class":
        index_file = INDEX_DIR / "class_hierarchy.csv"
        child_ns_col = "child_namespace"
        child_name_col = "child_class"
        parent_ns_col = "parent_namespace"
        parent_name_col = "parent_class"
    elif category == "interface":
        index_file = INDEX_DIR / "interface_hierarchy.csv"
        child_ns_col = "child_namespace"
        child_name_col = "child_interface"
        parent_ns_col = "parent_namespace"
        parent_name_col = "parent_interface"
    else:
        print("NO-MATCHES")
        return

    if not index_file.exists():
        print("NO-MATCHES")
        return

    matches = []
    with open(index_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if ns_filter:
                row_ns = row[child_ns_col].lower()
                if not (row_ns == ns_filter or row_ns.startswith(ns_filter + ".")):
                    continue
            child_name = row[child_name_col]
            if all(matches_pattern(child_name, p) for p in patterns):
                child_fqn = f"{row[child_ns_col]}.{child_name}" if row[child_ns_col] else child_name
                parent_fqn = f"{row[parent_ns_col]}.{row[parent_name_col]}" if row[parent_ns_col] else row[parent_name_col]
                matches.append((child_fqn, parent_fqn))

    matches.sort()
    return matches


def search_hierarchy_children(category, patterns, ns_filter):
    """Search for children classes/interfaces of matching parents"""
    if category == "class":
        index_file = INDEX_DIR / "class_hierarchy.csv"
        child_ns_col = "child_namespace"
        child_name_col = "child_class"
        parent_ns_col = "parent_namespace"
        parent_name_col = "parent_class"
    elif category == "interface":
        index_file = INDEX_DIR / "interface_hierarchy.csv"
        child_ns_col = "child_namespace"
        child_name_col = "child_interface"
        parent_ns_col = "parent_namespace"
        parent_name_col = "parent_interface"
    else:
        print("NO-MATCHES")
        return

    if not index_file.exists():
        print("NO-MATCHES")
        return

    parent_children = defaultdict(list)
    with open(index_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parent_name = row[parent_name_col]
            if all(matches_pattern(parent_name, p) for p in patterns):
                if ns_filter:
                    row_ns = row[parent_ns_col].lower()
                    if not (row_ns == ns_filter or row_ns.startswith(ns_filter + ".")):
                        continue
                parent_fqn = f"{row[parent_ns_col]}.{parent_name}" if row[parent_ns_col] else parent_name
                child_fqn = f"{row[child_ns_col]}.{row[child_name_col]}" if row[child_ns_col] else row[child_name_col]
                parent_children[parent_fqn].append(child_fqn)

    matches = []
    for parent_fqn in sorted(parent_children.keys()):
        children = sorted(parent_children[parent_fqn])
        matches.append((parent_fqn, children))

    return matches


def search_class_implements(patterns, ns_filter):
    """Search for interfaces implemented by matching classes"""
    index_file = INDEX_DIR / "interface_implementation.csv"

    if not index_file.exists():
        print("NO-MATCHES")
        return

    matches = []
    with open(index_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if ns_filter:
                row_ns = row["implementing_namespace"].lower()
                if not (row_ns == ns_filter or row_ns.startswith(ns_filter + ".")):
                    continue
            impl_type = row["implementing_type"]
            if all(matches_pattern(impl_type, p) for p in patterns):
                impl_fqn = f"{row['implementing_namespace']}.{impl_type}" if row['implementing_namespace'] else impl_type
                interfaces = row["interfaces"]
                matches.append((impl_fqn, interfaces))

    matches.sort()
    return matches


def compress_namespace_hierarchy(fqn_list):
    """Group types by their full namespace path and format with single-level nesting."""
    if not fqn_list:
        return []

    namespace_groups = defaultdict(list)

    for fqn in fqn_list:
        if "." in fqn:
            namespace, type_name = fqn.rsplit(".", 1)
            namespace_groups[namespace].append(type_name)
        else:
            namespace_groups[""].append(fqn)

    results = []
    for namespace in sorted(namespace_groups.keys()):
        types = sorted(namespace_groups[namespace])

        if len(types) == 1:
            if namespace:
                results.append(f"{namespace}.{types[0]}")
            else:
                results.append(types[0])
        else:
            types_str = ",".join(types)
            if namespace:
                results.append(f"{namespace}.({types_str})")
            else:
                results.append(f"({types_str})")

    return results


def search_interface_implementors(patterns, ns_filter):
    """Search for classes implementing matching interfaces"""
    index_file = INDEX_DIR / "interface_implementation.csv"

    if not index_file.exists():
        print("NO-MATCHES")
        return

    interface_implementors = defaultdict(list)
    with open(index_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            interfaces = row["interfaces"].split(",")
            impl_fqn = f"{row['implementing_namespace']}.{row['implementing_type']}" if row['implementing_namespace'] else row['implementing_type']

            for iface_fqn in interfaces:
                iface_fqn = iface_fqn.strip()
                iface_name = iface_fqn.split(".")[-1] if "." in iface_fqn else iface_fqn

                if all(matches_pattern(iface_name, p) for p in patterns):
                    if ns_filter:
                        iface_ns = iface_fqn.rsplit(".", 1)[0] if "." in iface_fqn else ""
                        if iface_ns:
                            if not (iface_ns.lower() == ns_filter or iface_ns.lower().startswith(ns_filter + ".")):
                                continue

                    interface_implementors[iface_fqn].append(impl_fqn)

    matches = []
    for iface_fqn in sorted(interface_implementors.keys()):
        implementors = sorted(interface_implementors[iface_fqn])
        matches.append((iface_fqn, implementors))

    return matches


def main():
    args = parse_args()

    # Check if index exists
    if not INDEX_DIR.exists():
        print("ERROR: ModCodeIndex not found. Run index_mods.py first.", file=sys.stderr)
        sys.exit(1)

    # Check if this is a method signature query
    if args.category == "method" and args.symbol_type in METHOD_SUBCOMMANDS:
        if args.symbol_type == "signature":
            index_file = INDEX_DIR / "method_signatures.csv"

            if not index_file.exists():
                print("NO-MATCHES")
                sys.exit(0)

            patterns = [compile_pattern(p, args.case_insensitive) for p in args.patterns]
            ns_filter = args.namespace.lower() if args.namespace else ""

            matches = []
            with open(index_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if ns_filter:
                        row_ns = row["namespace"].lower()
                        if not (row_ns == ns_filter or row_ns.startswith(ns_filter + ".")):
                            continue
                    name = get_symbol_name(row, is_signature=True)
                    if all(matches_pattern(name, p) for p in patterns):
                        matches.append(row)

            if not matches:
                print("NO-MATCHES")
                sys.exit(0)

            if args.count:
                print(len(matches))
                sys.exit(0)

            matches.sort(key=lambda row: get_sort_key(row, is_signature=True))

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
                print(f"{location}|{row['signature']}")

            sys.exit(0)

    # Check if this is a hierarchy query
    if args.symbol_type in HIERARCHY_SUBCOMMANDS:
        patterns = [compile_pattern(p, args.case_insensitive) for p in args.patterns]
        ns_filter = args.namespace.lower() if args.namespace else ""

        if args.symbol_type == "parent":
            matches = search_hierarchy_parent(args.category, patterns, ns_filter)
        elif args.symbol_type == "children":
            matches = search_hierarchy_children(args.category, patterns, ns_filter)
        elif args.symbol_type == "implements":
            if args.category != "class":
                print("NO-MATCHES")
                sys.exit(0)
            matches = search_class_implements(patterns, ns_filter)
        elif args.symbol_type == "implementors":
            if args.category != "interface":
                print("NO-MATCHES")
                sys.exit(0)
            matches = search_interface_implementors(patterns, ns_filter)
        else:
            print("NO-MATCHES")
            sys.exit(0)

        if not matches:
            print("NO-MATCHES")
            sys.exit(0)

        if args.count:
            print(len(matches))
            sys.exit(0)

        if args.offset > 0:
            matches = matches[args.offset:]
        if args.limit > 0:
            matches = matches[:args.limit]

        for match in matches:
            if args.symbol_type in ("parent", "implements"):
                print(f"{match[0]}:{match[1]}")
            else:
                compressed_list = compress_namespace_hierarchy(match[1])
                for compressed in compressed_list:
                    print(f"{match[0]}|{compressed}")

        sys.exit(0)

    # Standard declaration/usage search
    if args.symbol_type not in ["declaration", "usage"]:
        print(f"Error: Invalid symbol_type '{args.symbol_type}'. Must be 'declaration', 'usage', or one of: {', '.join(HIERARCHY_SUBCOMMANDS | METHOD_SUBCOMMANDS)}", file=sys.stderr)
        sys.exit(1)

    decl_file, usage_file = CATEGORY_FILES[args.category]

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

    patterns = [compile_pattern(p, args.case_insensitive) for p in args.patterns]
    ns_filter = args.namespace.lower() if args.namespace else ""

    strip_generics = (
        args.symbol_type == "declaration"
        and args.category in ("class", "struct", "interface", "enum")
    )

    matches = []
    with open(index_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if ns_filter:
                row_ns = row["namespace"].lower()
                if not (row_ns == ns_filter or row_ns.startswith(ns_filter + ".")):
                    continue
            name = get_symbol_name(row, is_signature=False, strip_generics=strip_generics)

            if strip_generics and is_mangled_name(row.get("declaring_type", "")):
                if all(matches_pattern_prefix(name, p) for p in patterns):
                    matches.append(row)
            elif all(matches_pattern(name, p) for p in patterns):
                matches.append(row)

    if not matches:
        print("NO-MATCHES")
        sys.exit(0)

    if args.count:
        print(len(matches))
        sys.exit(0)

    matches.sort(key=lambda row: get_sort_key(row, is_signature=False))

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
        print(location)


if __name__ == "__main__":
    main()
