#!/usr/bin/env python3
"""
Content File Indexer

Builds a CSV index of all textual content files in the game's Content/ directory.
For each content file, emits one row per C# source file that references it.
Content files with no usages get a single row with an empty usage column.

Usage:
    python index_content.py <content_dir> <decompiled_dir> <output_dir>

Example:
    python index_content.py Content Decompiled CodeIndex
"""

import csv
import os
import re
import sys
from pathlib import Path

# Matches identifier-like tokens, optionally with dotted segments.
# Examples: "CubeBlocks_Armor", "CubeBlocks_Armor.sbc", "Foo.Bar.Baz".
# Quotes, slashes, backslashes, and whitespace all break tokens, so a string
# literal like "Data/CubeBlocks_Armor.sbc" yields "Data" and "CubeBlocks_Armor.sbc".
TOKEN_RE = re.compile(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*")

# Characters allowed inside a token. Patterns containing anything else (spaces,
# parens, etc.) cannot match token-substring scanning and need a raw-text fallback.
TOKEN_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.")

# Text file extensions to index (skip binary assets like .dds, .mwm, .wav, etc.)
TEXT_EXTENSIONS = {
    ".sbc", ".hlsl", ".hlsli", ".resx", ".vs", ".scf", ".xml", ".sbl",
    ".txt", ".ini", ".cfg", ".json", ".fx", ".fxh",
}


def collect_content_files(content_dir):
    """Walk Content/ and collect all text-based content files."""
    files = []
    for root, _, filenames in os.walk(content_dir):
        for fname in filenames:
            full = Path(root) / fname
            if full.suffix.lower() in TEXT_EXTENSIONS:
                rel = full.relative_to(content_dir)
                files.append(str(rel).replace("\\", "/"))
    files.sort()
    return files


def build_source_text_cache(decompiled_dir):
    """Read all decompiled .cs files into a dict keyed by relative path."""
    cache = {}
    for root, _, filenames in os.walk(decompiled_dir):
        for fname in filenames:
            if not fname.endswith(".cs"):
                continue
            full = Path(root) / fname
            rel = str(full.relative_to(decompiled_dir)).replace("\\", "/")
            try:
                cache[rel] = full.read_text(encoding="utf-8-sig", errors="replace")
            except Exception:
                pass
    return cache


def build_token_index(source_cache):
    """Build inverted index: token -> set of source rel_paths containing it.

    Each source file is tokenized once into identifier-like tokens (with optional
    dotted segments). The set of unique tokens is dramatically smaller than the
    raw 100+ MB corpus, so the per-pattern substring scan in find_usages becomes
    cheap.
    """
    index = {}
    for rel_path, text in source_cache.items():
        for token in set(TOKEN_RE.findall(text)):
            index.setdefault(token, set()).add(rel_path)
    return index


def find_usages(filename_stem, filename_full, token_index, tokens, source_cache):
    """Find C# source files that reference this content filename.

    Substring semantics match the original `pat in text` behavior: a pattern
    matches if it appears anywhere inside any token (so stem "AlienSystem"
    still matches inside identifier "CustomWorld_AlienSystem"). Patterns that
    contain non-token characters (e.g. spaces in "Learning to Survive") fall
    back to scanning raw source text, since they can never sit inside a single
    token.
    """
    patterns = [filename_full]
    # Stem-only match is permissive, so require >= 6 chars to limit collisions.
    if len(filename_stem) >= 6:
        patterns.append(filename_stem)

    fast_pats = [p for p in patterns if all(c in TOKEN_CHARS for c in p)]
    slow_pats = [p for p in patterns if p not in fast_pats]

    matches = set()
    if fast_pats:
        for tok in tokens:
            for pat in fast_pats:
                if pat in tok:
                    matches.update(token_index[tok])
                    break
    if slow_pats:
        for rel_path, text in source_cache.items():
            for pat in slow_pats:
                if pat in text:
                    matches.add(rel_path)
                    break
    return sorted(matches)


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <content_dir> <decompiled_dir> <output_dir>")
        sys.exit(1)

    content_dir = Path(sys.argv[1])
    decompiled_dir = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    output_file = output_dir / "content_index.csv"

    print("Collecting content files...")
    files = collect_content_files(content_dir)
    print(f"  Found {len(files)} text content files")

    print("Loading decompiled source cache...")
    source_cache = build_source_text_cache(decompiled_dir)
    print(f"  Loaded {len(source_cache)} source files")

    print("Building token index...")
    token_index = build_token_index(source_cache)
    tokens = list(token_index.keys())
    print(f"  Indexed {len(tokens)} unique tokens")

    print("Searching for usages...")
    rows = []
    usage_count = 0
    for rel_path in files:
        fname = Path(rel_path).name
        stem = Path(rel_path).stem
        usages = find_usages(stem, fname, token_index, tokens, source_cache)
        usage_count += len(usages)
        if usages:
            for usage in usages:
                rows.append({"rel_path": rel_path, "usage": usage})
        else:
            rows.append({"rel_path": rel_path, "usage": ""})

    print(f"  Found {usage_count} total usage references across {len(files)} content files")

    os.makedirs(output_dir, exist_ok=True)
    print(f"Writing {output_file}...")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["rel_path", "usage"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. {len(rows)} rows written to {output_file}")


if __name__ == "__main__":
    main()
