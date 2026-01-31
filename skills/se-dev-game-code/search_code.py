#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from collections import defaultdict
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

HIERARCHY_SUBCOMMANDS = {"parent", "children", "implements", "implementors"}

def parse_args():
    parser = argparse.ArgumentParser(description="Search C# code index")
    parser.add_argument("-c", "--count", action="store_true", help="Print only the count of matches")
    parser.add_argument("-l", "--limit", type=int, default=0, help="Limit number of results")
    parser.add_argument("-o", "--offset", type=int, default=0, help="Skip first N results")
    parser.add_argument("-n", "--namespace", type=str, default="", help="Filter by namespace prefix")
    parser.add_argument("category", choices=list(CATEGORY_FILES.keys()), help="Symbol category")
    parser.add_argument("symbol_type", help="Symbol type (declaration/usage) or hierarchy subcommand (parent/children/implements/implementors)")
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
    
    # Build parent -> children map
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
    
    # Sort and format results
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
    """
    Compress a list of fully-qualified names into hierarchical namespace structure.
    
    Example input: ['A.B.C.Class1', 'A.B.C.Class2', 'A.B.D.Class3', 'X.Y.Class4']
    Example output: 'A.B.(C.(Class1,Class2),D.Class3),X.Y.Class4'
    """
    if not fqn_list:
        return ""
    
    # Parse FQNs into namespace path + class name
    parsed = []
    for fqn in fqn_list:
        parts = fqn.split(".")
        if len(parts) == 1:
            # No namespace, just class name
            parsed.append(([], parts[0]))
        else:
            # namespace parts + class name
            parsed.append((parts[:-1], parts[-1]))
    
    # Build a tree structure
    def build_tree(items):
        """Build a nested dict tree from (namespace_parts, class_name) tuples"""
        tree = {}
        for ns_parts, class_name in items:
            if not ns_parts:
                # Top-level class (no namespace)
                tree[class_name] = None
            else:
                # Has namespace - group by first namespace part
                first_ns = ns_parts[0]
                if first_ns not in tree:
                    tree[first_ns] = []
                tree[first_ns].append((ns_parts[1:], class_name))
        
        # Recursively build subtrees for namespace groups
        result = {}
        for key, value in tree.items():
            if value is None:
                # Leaf node (class name)
                result[key] = None
            else:
                # Namespace node - recurse
                result[key] = build_tree(value)
        
        return result
    
    def format_tree(tree, depth=0):
        """Format tree into compressed string representation"""
        if not tree:
            return ""
        
        parts = []
        for key in sorted(tree.keys()):
            value = tree[key]
            if value is None:
                # Leaf node (class name)
                parts.append(key)
            else:
                # Namespace node - try to flatten single-child chains
                flattened = flatten_single_chain(key, value)
                if flattened:
                    # Was able to flatten into dotted path
                    parts.append(flattened)
                else:
                    # Has multiple children - use parentheses
                    children_str = format_tree(value, depth + 1)
                    parts.append(f"{key}.({children_str})")
        
        return ",".join(parts)
    
    def flatten_single_chain(prefix, subtree):
        """
        Try to flatten a single-child chain into a dotted path.
        Returns the flattened string or None if can't flatten.
        """
        if len(subtree) != 1:
            return None
        
        child_key = list(subtree.keys())[0]
        child_value = subtree[child_key]
        
        if child_value is None:
            # Single leaf child - flatten
            return f"{prefix}.{child_key}"
        else:
            # Single namespace child - recurse
            flattened_child = flatten_single_chain(child_key, child_value)
            if flattened_child:
                return f"{prefix}.{flattened_child}"
            else:
                # Child has multiple children, can't flatten further
                return None
    
    tree = build_tree(parsed)
    return format_tree(tree)

def search_interface_implementors(patterns, ns_filter):
    """Search for classes implementing matching interfaces"""
    index_file = INDEX_DIR / "interface_implementation.csv"
    
    if not index_file.exists():
        print("NO-MATCHES")
        return
    
    # Build interface -> implementors map
    interface_implementors = defaultdict(list)
    with open(index_file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            interfaces = row["interfaces"].split(",")
            impl_fqn = f"{row['implementing_namespace']}.{row['implementing_type']}" if row['implementing_namespace'] else row['implementing_type']
            
            for iface_fqn in interfaces:
                iface_fqn = iface_fqn.strip()
                # Extract just the interface name for pattern matching
                iface_name = iface_fqn.split(".")[-1] if "." in iface_fqn else iface_fqn
                
                if all(matches_pattern(iface_name, p) for p in patterns):
                    # Apply namespace filter to interface
                    if ns_filter:
                        iface_ns = iface_fqn.rsplit(".", 1)[0] if "." in iface_fqn else ""
                        if iface_ns:
                            if not (iface_ns.lower() == ns_filter or iface_ns.lower().startswith(ns_filter + ".")):
                                continue
                    
                    interface_implementors[iface_fqn].append(impl_fqn)
    
    # Sort and format results
    matches = []
    for iface_fqn in sorted(interface_implementors.keys()):
        implementors = sorted(interface_implementors[iface_fqn])
        matches.append((iface_fqn, implementors))
    
    return matches

def main():
    args = parse_args()
    
    # Check if this is a hierarchy query
    if args.symbol_type in HIERARCHY_SUBCOMMANDS:
        patterns = [compile_pattern(p) for p in args.patterns]
        ns_filter = args.namespace.lower() if args.namespace else ""
        
        # Route to appropriate hierarchy handler
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
        
        # Apply offset and limit
        if args.offset > 0:
            matches = matches[args.offset:]
        if args.limit > 0:
            matches = matches[:args.limit]
        
        # Output results
        for match in matches:
            if args.symbol_type in ("parent", "implements"):
                # One-to-one: child:parent or class:interfaces
                print(f"{match[0]}:{match[1]}")
            else:  # children or implementors
                # One-to-many: parent|child1,child2,...
                compressed = compress_namespace_hierarchy(match[1])
                print(f"{match[0]}|{compressed}")
        
        sys.exit(0)
    
    # Standard declaration/usage search
    if args.symbol_type not in ["declaration", "usage"]:
        print(f"Error: Invalid symbol_type '{args.symbol_type}'. Must be 'declaration', 'usage', or one of: {', '.join(HIERARCHY_SUBCOMMANDS)}", file=sys.stderr)
        sys.exit(1)
    
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
