#!/usr/bin/env python3
"""
Helper module for generating hierarchy tree text files.
"""

from collections import defaultdict
from typing import Dict, List, Set, Tuple


def build_class_tree(hierarchy_entries: List[Tuple[str, str, str, str]]) -> str:
    """
    Build a tree-style text representation of class hierarchy.

    Args:
        hierarchy_entries: List of (child_ns, child_class, parent_ns, parent_class) tuples

    Returns:
        Tree text with box-drawing characters
    """
    # Build parent->children map
    children_map: Dict[str, List[str]] = defaultdict(list)
    all_types: Set[str] = set()

    for child_ns, child_class, parent_ns, parent_class in hierarchy_entries:
        child_fqn = f"{child_ns}.{child_class}" if child_ns else child_class
        parent_fqn = f"{parent_ns}.{parent_class}" if parent_ns else parent_class

        children_map[parent_fqn].append(child_fqn)
        all_types.add(child_fqn)
        all_types.add(parent_fqn)

    # Sort children lists
    for parent in children_map:
        children_map[parent].sort()

    # Find roots (types that are not children of anything)
    roots = sorted([t for t in all_types if t not in [c for children in children_map.values() for c in children]])

    # Build tree text
    lines = []
    visited = set()

    def add_node(fqn: str, prefix: str, is_last: bool):
        if fqn in visited:
            return  # Avoid cycles
        visited.add(fqn)

        # Add current node
        if prefix:
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix[:-4]}{connector}{fqn}")
        else:
            lines.append(fqn)

        # Add children
        children = children_map.get(fqn, [])
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            if prefix:
                child_prefix = prefix[:-4] + ("    " if is_last else "│   ") + "    "
            else:
                child_prefix = "    "
            add_node(child, child_prefix, is_last_child)

    # Process each root
    for i, root in enumerate(roots):
        if i > 0:
            lines.append("")  # Blank line between trees
        add_node(root, "", i == len(roots) - 1)

    return "\n".join(lines)


def build_interface_tree(hierarchy_entries: List[Tuple[str, str, str, str]]) -> str:
    """
    Build a tree-style text representation of interface hierarchy.

    Args:
        hierarchy_entries: List of (child_ns, child_iface, parent_ns, parent_iface) tuples

    Returns:
        Tree text with box-drawing characters
    """
    # Same logic as class tree
    return build_class_tree(hierarchy_entries)
