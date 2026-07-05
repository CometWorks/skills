#!/usr/bin/env python3
"""Analyze Mod API whitelist to show available namespaces."""

from collections import Counter

with open('ModApiWhitelist.txt', 'r') as f:
    lines = f.readlines()

# Extract top-level namespaces
namespaces = []
for line in lines:
    parts = line.strip().split(',')
    if parts:
        ns_parts = parts[0].split('.')
        if len(ns_parts) >= 2:
            namespaces.append(f"{ns_parts[0]}.{ns_parts[1]}")

# Count occurrences
ns_counts = Counter(namespaces)

print("Mod API Whitelist - Available Namespaces:\n")
print(f"{'Namespace':<40} {'Count':<10}")
print("=" * 50)

for ns, count in sorted(ns_counts.items()):
    print(f"{ns:<40} {count:<10}")

print(f"\nTotal unique namespaces: {len(ns_counts)}")
print(f"Total API entries: {len(lines)}")
