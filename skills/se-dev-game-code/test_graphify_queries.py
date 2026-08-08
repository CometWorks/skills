#!/usr/bin/env python3
"""Graphify query smoke test for a decompiled code graph.

Usage: test_graphify_queries.py <dir containing graphify-out>

The platform wrapper (`test_graphify_*_code.sh` / `.bat`) runs the health check
and passes the graph directory here. Every query asserts its outcome instead of
only printing it, and `explain` additionally asserts that the name resolved to a
real source-backed node: fuzzy matching happily settles on a stub node that
carries no source location and a single edge, which looks like a successful
answer but tells you nothing.

Exits non-zero if any check failed.
"""

import subprocess
import sys
from pathlib import Path

BANNER = "=" * 60

# Argument lists passed to `graphify`, grouped into printed sections.
QUERIES = [
    ("section", "QUERY - BFS traversal for a question"),
    ("query", ["query", "How is a cube grid built and updated?", "--budget", "400"]),
    ("query", ["query", "How does a projector project a blueprint?", "--budget", "400"]),

    ("section", "QUERY - narrowed by edge context"),
    ("query", ["query", "MyCubeGrid", "--context", "call", "--budget", "300"]),

    ("section", "EXPLAIN - a node and its neighbours"),
    ("explain", ["explain", "MyProgrammableBlock"]),
    ("explain", ["explain", "MyEntity"]),

    ("section", "PATH - shortest path between two nodes"),
    ("path", ["path", "MyCubeBlock", "MyEntity"]),

    ("section", "AFFECTED - reverse traversal for impact"),
    ("affected", ["affected", "MyEntity", "--depth", "1"]),
]


def section(title):
    print(BANNER)
    print(title)
    print(BANNER)


def run_graphify(graph_dir, args):
    result = subprocess.run(
        ["graphify", *args], cwd=graph_dir, capture_output=True, text=True
    )
    return (result.stdout + result.stderr).strip()


def check_output(kind, output):
    """Return a problem description, or None when the output looks usable."""
    if not output:
        return "no output"
    if "No matching nodes found" in output:
        return "no matching nodes"
    if kind == "explain":
        # A resolved node must be backed by a source location; a bare stub means
        # the fuzzy match landed on a placeholder rather than the real symbol.
        for line in output.splitlines():
            if line.strip().startswith("Source:"):
                if line.split(":", 1)[1].strip():
                    return None
                return "resolved to a node without a source location"
        return "no Source line in explain output"
    if kind == "path" and "Shortest path" not in output:
        return "no path found"
    return None


def main():
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} <dir containing graphify-out>")
        return 2

    graph_dir = Path(sys.argv[1]).resolve()
    if not (graph_dir / "graphify-out").is_dir():
        print(f"FATAL: no graphify-out directory under {graph_dir}")
        return 2

    checks = 0
    failures = []

    for kind, payload in QUERIES:
        if kind == "section":
            section(payload)
            continue

        checks += 1
        title = " ".join(payload)
        print(f"--- {title} ---")
        output = run_graphify(graph_dir, payload)
        print(output)

        problem = check_output(kind, output)
        if problem:
            print(f"FAIL: {problem}")
            failures.append(f"{title}: {problem}")
        print()

    section("SUMMARY")
    print(f"Checks run: {checks}")
    print(f"Failures:   {len(failures)}")
    print()
    if failures:
        for failure in failures:
            print(f"FAILED - {failure}")
        print()
        section("TESTS FAILED")
        return 1

    section("ALL TESTS COMPLETED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
