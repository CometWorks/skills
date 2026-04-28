#!/usr/bin/env python3
"""
Mod Code Index — incremental orchestrator.

Reads the inventory produced by list_mods.py and indexes the C# code from
each mod with scripts. Mods are tagged in every CSV row by prefixing
file_path with "<workshop_id>/...", which lets us cheaply carry over rows
for unchanged mods on the next run.

Incremental flow:

  1. Compute an aggregate sha1 per mod over the sorted list of
     (relative_path, sha1(content)) tuples for its .cs files.
  2. Compare against mod_hashes.json (last run's hashes).
  3. Mods are bucketed as unchanged / changed / new / removed.
  4. Existing CSVs are loaded; rows whose mod is changed or removed
     are dropped; rows for unchanged mods are kept verbatim.
  5. Changed and new mods are reparsed (two-pass: declarations, then
     usages with the merged declared-name table).
  6. Carried-over rows + freshly parsed rows are merged, sorted, and
     written out. Hierarchy text trees are regenerated from the merged
     hierarchy CSV data.
  7. mod_hashes.json is updated.

If no prior CSVs exist, this degenerates to a full rebuild.
"""

import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cs_indexer import (
    CLASS_HIERARCHY_FILE,
    ClassHierarchyEntry,
    FileProcessingResult,
    FileProcessor,
    INDEX_ENTRY_FILES,
    INTERFACE_HIERARCHY_FILE,
    INTERFACE_IMPL_FILE,
    IndexEntry,
    InterfaceHierarchyEntry,
    InterfaceImplementationEntry,
    SIGNATURE_FILE,
    SignatureEntry,
)
from hierarchy_tree import build_class_tree, build_interface_tree
from mod_paths import CODE_INDEX_DIR, MOD_HASHES_FILE, MOD_LIST_FILE


# Per-category index file basenames (declarations + usages).
CATEGORIES = [
    'namespace', 'interface', 'class', 'struct', 'enum',
    'method', 'field', 'property', 'event', 'constructor',
]

BATCH_SIZE = 32


# --------------------------------------------------------------------------
# Mod-level helpers
# --------------------------------------------------------------------------

def _mod_root_for_scan(mod: Dict) -> Path:
    """Folder under which to find a mod's .cs files."""
    base = Path(mod["path"])
    if mod["source"] == "steam":
        return base / "Data" / "Scripts"
    return base


def _collect_mod_files(mod: Dict) -> List[Tuple[Path, str]]:
    """Return [(absolute_path, relative_path_within_mod), ...] for the mod."""
    root = _mod_root_for_scan(mod)
    if not root.exists():
        return []
    pairs: List[Tuple[Path, str]] = []
    for cs_file in root.rglob("*.cs"):
        if not cs_file.is_file():
            continue
        rel = cs_file.relative_to(root).as_posix()
        pairs.append((cs_file, rel))
    pairs.sort(key=lambda p: p[1])
    return pairs


def _hash_mod(files: List[Tuple[Path, str]]) -> str:
    """Aggregate sha1 over sorted (rel_path, sha1(content)) tuples."""
    h = hashlib.sha1()
    for abs_path, rel_path in files:
        try:
            content = abs_path.read_bytes()
        except OSError:
            continue
        file_hash = hashlib.sha1(content).hexdigest()
        h.update(rel_path.encode("utf-8"))
        h.update(b"\0")
        h.update(file_hash.encode("ascii"))
        h.update(b"\0")
    return h.hexdigest()


def _label_for_mod(mod: Dict) -> str:
    """Path-label prefix used for every CSV row produced from this mod.

    The leading component is workshop_id (numeric for Steam, folder name for
    local). That's what we partition on when carrying over unchanged rows.
    """
    return mod["workshop_id"]


def _mod_label_from_row_path(file_path: str) -> Optional[str]:
    """Extract the leading path component (= workshop_id) from a CSV row."""
    if not file_path:
        return None
    norm = file_path.replace("\\", "/")
    head, _, _ = norm.partition("/")
    return head or None


# --------------------------------------------------------------------------
# Worker (parallel parsing)
# --------------------------------------------------------------------------

def _process_batch_worker(args: Tuple) -> List[FileProcessingResult]:
    """Parse a batch of files with one FileProcessor in a subprocess."""
    items, collect_usages, shared_declarations = args

    sys.setrecursionlimit(10000)
    processor = FileProcessor(root_path=".")

    if collect_usages and shared_declarations:
        processor.declared_namespaces = shared_declarations['namespaces']
        processor.declared_interfaces = shared_declarations['interfaces']
        processor.declared_classes = shared_declarations['classes']
        processor.declared_structs = shared_declarations['structs']
        processor.declared_enums = shared_declarations['enums']
        processor.declared_methods = shared_declarations['methods']
        processor.declared_properties = shared_declarations['properties']
        processor.declared_events = shared_declarations['events']
        processor.declared_constructors = shared_declarations['constructors']

    results: List[FileProcessingResult] = []
    for abs_path, path_label in items:
        try:
            results.append(processor.process_file(
                Path(abs_path), collect_usages, path_label=path_label,
            ))
        except Exception as exc:  # noqa: BLE001
            print(f"Error processing {abs_path}: {exc}", file=sys.stderr)
            results.append(FileProcessingResult())
    return results


def _batch(items: List, size: int) -> List[List]:
    return [items[i:i + size] for i in range(0, len(items), size)]


# --------------------------------------------------------------------------
# Existing-CSV row carry-over
# --------------------------------------------------------------------------

def _load_csv_rows(path: Path) -> Tuple[List[str], List[List[str]]]:
    """Return (header, rows). If the file is missing, both are empty."""
    if not path.exists():
        return [], []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return [], []
        rows = [row for row in reader]
    return header, rows


def _file_path_column_index(header: List[str]) -> Optional[int]:
    try:
        return header.index("file_path")
    except ValueError:
        return None


def _carry_over_rows(
    csv_path: Path,
    keep_labels: Set[str],
) -> List[List[str]]:
    """Load CSV rows whose mod label is in keep_labels."""
    header, rows = _load_csv_rows(csv_path)
    if not header or not rows:
        return []
    fp_idx = _file_path_column_index(header)
    if fp_idx is None:
        return []
    kept: List[List[str]] = []
    for row in rows:
        if fp_idx >= len(row):
            continue
        label = _mod_label_from_row_path(row[fp_idx])
        if label in keep_labels:
            kept.append(row)
    return kept


# Maps each *_declarations.csv basename to the (declared_*-key, name_column).
# `name_column` is the CSV column index whose value is the declared name we
# need to seed pass 2's usage-detection sets with.
_DECL_FILE_TO_BUCKET: Dict[str, Tuple[str, int]] = {
    'namespace_declarations.csv': ('namespaces', 0),    # namespace column
    'interface_declarations.csv': ('interfaces', 1),    # declaring_type
    'class_declarations.csv':     ('classes', 1),
    'struct_declarations.csv':    ('structs', 1),
    'enum_declarations.csv':      ('enums', 1),
    'method_declarations.csv':    ('methods', 2),       # method
    'property_declarations.csv':  ('properties', 3),    # symbol_name
    'event_declarations.csv':     ('events', 3),
    'constructor_declarations.csv': ('constructors', 2),
}


def _seed_declarations_from_csvs(
    keep_labels: Set[str],
    declared: Dict,
) -> None:
    """Seed the declared_* sets from carried-over declarations of unchanged mods.

    Pass 2 of the changed/new mods needs to know about types declared in
    unchanged mods so that cross-mod references are still classified as
    usages. We seed the sets directly from the existing declaration CSVs,
    filtered to rows whose mod label is unchanged.
    """
    if not keep_labels:
        return
    for fname, (bucket, name_col) in _DECL_FILE_TO_BUCKET.items():
        csv_path = CODE_INDEX_DIR / fname
        header, rows = _load_csv_rows(csv_path)
        if not header or not rows:
            continue
        fp_idx = _file_path_column_index(header)
        if fp_idx is None:
            continue
        for row in rows:
            if fp_idx >= len(row) or name_col >= len(row):
                continue
            label = _mod_label_from_row_path(row[fp_idx])
            if label not in keep_labels:
                continue
            name = row[name_col]
            if not name:
                continue
            if bucket == 'namespaces':
                declared['namespaces'].add(name)
            else:
                ns = row[0] if len(row) > 0 else ''
                declared[bucket][name].add((ns, ''))


# --------------------------------------------------------------------------
# Main orchestrator
# --------------------------------------------------------------------------

class ModIndexRun:
    def __init__(self):
        self.mods: List[Dict] = []
        self.mod_files: Dict[str, List[Tuple[Path, str]]] = {}
        self.new_hashes: Dict[str, str] = {}
        self.old_hashes: Dict[str, str] = {}
        self.unchanged_labels: Set[str] = set()
        self.changed_or_new_labels: Set[str] = set()

        self.num_workers = max(1, cpu_count() * 2)

    # ----- inventory & hashing -------------------------------------------------

    def load_inventory(self) -> None:
        if not MOD_LIST_FILE.exists():
            print(f"ERROR: {MOD_LIST_FILE} not found. Run list_mods.py first.",
                  file=sys.stderr)
            sys.exit(1)
        with open(MOD_LIST_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.mods = [m for m in data.get("mods", []) if m.get("has_scripts")]
        print(f"Inventory: {len(self.mods)} mods with scripts.")

    def hash_mods(self) -> None:
        for mod in self.mods:
            label = _label_for_mod(mod)
            files = _collect_mod_files(mod)
            self.mod_files[label] = files
            self.new_hashes[label] = _hash_mod(files)

    def load_old_hashes(self) -> None:
        if not MOD_HASHES_FILE.exists():
            return
        try:
            with open(MOD_HASHES_FILE, "r", encoding="utf-8") as f:
                self.old_hashes = json.load(f).get("hashes", {})
        except (OSError, json.JSONDecodeError):
            self.old_hashes = {}

    def diff_mods(self) -> None:
        for label, new_hash in self.new_hashes.items():
            if self.old_hashes.get(label) == new_hash:
                self.unchanged_labels.add(label)
            else:
                self.changed_or_new_labels.add(label)

        removed = set(self.old_hashes) - set(self.new_hashes)
        unchanged = len(self.unchanged_labels)
        changed_new = len(self.changed_or_new_labels)
        print(f"Diff: {unchanged} unchanged, {changed_new} changed/new, "
              f"{len(removed)} removed.")

    # ----- parsing -------------------------------------------------------------

    def _files_to_parse(self) -> List[Tuple[str, str]]:
        """Return (absolute_path_str, path_label) pairs for mods needing parse."""
        items: List[Tuple[str, str]] = []
        for label in self.changed_or_new_labels:
            for abs_path, rel_path in self.mod_files.get(label, []):
                items.append((str(abs_path), f"{label}/{rel_path}"))
        return items

    def parse_changed(self) -> Optional[FileProcessingResult]:
        """Parse all changed/new mods. Returns merged FileProcessingResult."""
        items = self._files_to_parse()
        if not items:
            print("No mods need reparsing.")
            return None

        print(f"Parsing {len(items)} files from "
              f"{len(self.changed_or_new_labels)} changed/new mods...")
        random.shuffle(items)
        batches = _batch(items, BATCH_SIZE)

        # Pass 1: declarations
        print(f"  Pass 1 (declarations): {len(batches)} batches, "
              f"{self.num_workers} workers")
        pass1_args = [(b, False, None) for b in batches]
        with Pool(processes=self.num_workers) as pool:
            pass1_results = list(pool.imap_unordered(_process_batch_worker, pass1_args))

        merged = FileProcessingResult()
        declared = {
            'namespaces': set(),
            'interfaces': defaultdict(set), 'classes': defaultdict(set),
            'structs': defaultdict(set), 'enums': defaultdict(set),
            'methods': defaultdict(set), 'properties': defaultdict(set),
            'events': defaultdict(set), 'constructors': defaultdict(set),
        }
        for batch_results in pass1_results:
            for r in batch_results:
                _accumulate_result(merged, r)
                _accumulate_declarations(declared, r)

        # Cross-mod awareness: pull declarations of unchanged mods from
        # the existing CSVs so usages referencing them get classified.
        _seed_declarations_from_csvs(self.unchanged_labels, declared)

        # Convert defaultdicts to plain dicts for cross-process pickling
        shared_decls = {
            'namespaces': declared['namespaces'],
            'interfaces': dict(declared['interfaces']),
            'classes': dict(declared['classes']),
            'structs': dict(declared['structs']),
            'enums': dict(declared['enums']),
            'methods': dict(declared['methods']),
            'properties': dict(declared['properties']),
            'events': dict(declared['events']),
            'constructors': dict(declared['constructors']),
        }

        # Pass 2: usages
        print(f"  Pass 2 (usages): {len(batches)} batches")
        pass2_args = [(b, True, shared_decls) for b in batches]
        with Pool(processes=self.num_workers) as pool:
            pass2_results = list(pool.imap_unordered(_process_batch_worker, pass2_args))

        for batch_results in pass2_results:
            for r in batch_results:
                _accumulate_result(merged, r)

        return merged

    # ----- writing -------------------------------------------------------------

    def write_index(self, parsed: Optional[FileProcessingResult]) -> None:
        CODE_INDEX_DIR.mkdir(parents=True, exist_ok=True)

        keep_labels = self.unchanged_labels  # rows for these labels carry over

        # Build the per-category lists of new rows (just CSV rows, not entries)
        new_rows_by_file: Dict[str, List[List[str]]] = defaultdict(list)
        if parsed is not None:
            for category in CATEGORIES:
                attr = f"{category}_entries"
                entries: List[IndexEntry] = getattr(parsed, attr)
                decls = [e for e in entries if e.entry_type == 'declaration']
                usages = [e for e in entries if e.entry_type == 'usage']
                new_rows_by_file[f"{category}_declarations.csv"] = [
                    e.to_csv_row() for e in decls
                ]
                new_rows_by_file[f"{category}_usages.csv"] = [
                    e.to_csv_row() for e in usages
                ]
            new_rows_by_file[SIGNATURE_FILE] = [
                e.to_csv_row() for e in parsed.signature_entries
            ]
            new_rows_by_file[CLASS_HIERARCHY_FILE] = [
                e.to_csv_row() for e in parsed.class_hierarchy_entries
            ]
            new_rows_by_file[INTERFACE_HIERARCHY_FILE] = [
                e.to_csv_row() for e in parsed.interface_hierarchy_entries
            ]
            new_rows_by_file[INTERFACE_IMPL_FILE] = [
                e.to_csv_row() for e in parsed.interface_implementation_entries
            ]

        # Per-category headers
        headers: Dict[str, List[str]] = {}
        for fname in INDEX_ENTRY_FILES:
            headers[fname] = IndexEntry.csv_header()
        headers[SIGNATURE_FILE] = SignatureEntry.csv_header()
        headers[CLASS_HIERARCHY_FILE] = ClassHierarchyEntry.csv_header()
        headers[INTERFACE_HIERARCHY_FILE] = InterfaceHierarchyEntry.csv_header()
        headers[INTERFACE_IMPL_FILE] = InterfaceImplementationEntry.csv_header()

        # Sort keys (column indices) per file basename
        sort_keys: Dict[str, List[int]] = {}
        index_entry_sort = [0, 1, 2, 3, 5, 6, 7]  # ns, type, method, sym, fp, sl, el
        for fname in INDEX_ENTRY_FILES:
            sort_keys[fname] = index_entry_sort
        sort_keys[SIGNATURE_FILE] = [0, 1, 2, 4, 5, 6]  # ns, type, method, fp, sl, el
        sort_keys[CLASS_HIERARCHY_FILE] = [0, 1, 2, 3]
        sort_keys[INTERFACE_HIERARCHY_FILE] = [0, 1, 2, 3]
        sort_keys[INTERFACE_IMPL_FILE] = [0, 1, 2]

        all_files = (
            list(INDEX_ENTRY_FILES)
            + [SIGNATURE_FILE, CLASS_HIERARCHY_FILE,
               INTERFACE_HIERARCHY_FILE, INTERFACE_IMPL_FILE]
        )

        totals: Dict[str, int] = {}
        for fname in all_files:
            csv_path = CODE_INDEX_DIR / fname
            carried = _carry_over_rows(csv_path, keep_labels)
            new_rows = new_rows_by_file.get(fname, [])
            combined = carried + new_rows
            keys = sort_keys[fname]
            combined.sort(key=lambda r, ks=keys: tuple(
                _sort_value(r[k]) if k < len(r) else "" for k in ks
            ))
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers[fname])
                writer.writerows(combined)
            totals[fname] = len(combined)

        # Hierarchy tree text files (regenerate from merged hierarchy CSVs)
        self._write_hierarchy_trees()

        # Persist hashes
        with open(MOD_HASHES_FILE, "w", encoding="utf-8") as f:
            json.dump({"hashes": self.new_hashes}, f, indent=2)

        # Summary
        decls = sum(totals[f"{c}_declarations.csv"] for c in CATEGORIES)
        usages = sum(totals[f"{c}_usages.csv"] for c in CATEGORIES)
        print(f"\nIndex written to {CODE_INDEX_DIR}")
        print(f"  Declarations: {decls}")
        print(f"  Usages:       {usages}")
        print(f"  Signatures:   {totals[SIGNATURE_FILE]}")
        print(f"  Class hier:   {totals[CLASS_HIERARCHY_FILE]}")
        print(f"  Iface hier:   {totals[INTERFACE_HIERARCHY_FILE]}")
        print(f"  Iface impls:  {totals[INTERFACE_IMPL_FILE]}")

    def _write_hierarchy_trees(self) -> None:
        # Class tree
        class_csv = CODE_INDEX_DIR / CLASS_HIERARCHY_FILE
        _, rows = _load_csv_rows(class_csv)
        if rows:
            tuples = [(r[0], r[1], r[2], r[3]) for r in rows if len(r) >= 4]
            text = build_class_tree(tuples)
            (CODE_INDEX_DIR / "class_hierarchy.txt").write_text(text, encoding="utf-8")

        # Interface tree
        iface_csv = CODE_INDEX_DIR / INTERFACE_HIERARCHY_FILE
        _, rows = _load_csv_rows(iface_csv)
        if rows:
            tuples = [(r[0], r[1], r[2], r[3]) for r in rows if len(r) >= 4]
            text = build_interface_tree(tuples)
            (CODE_INDEX_DIR / "interface_hierarchy.txt").write_text(text, encoding="utf-8")


def _sort_value(s: str):
    """Sort numeric-looking strings as ints, otherwise as strings."""
    if s.isdigit():
        return (0, int(s))
    return (1, s)


def _accumulate_result(dst: FileProcessingResult, src: FileProcessingResult) -> None:
    dst.namespace_entries.extend(src.namespace_entries)
    dst.interface_entries.extend(src.interface_entries)
    dst.class_entries.extend(src.class_entries)
    dst.struct_entries.extend(src.struct_entries)
    dst.enum_entries.extend(src.enum_entries)
    dst.method_entries.extend(src.method_entries)
    dst.field_entries.extend(src.field_entries)
    dst.property_entries.extend(src.property_entries)
    dst.event_entries.extend(src.event_entries)
    dst.constructor_entries.extend(src.constructor_entries)
    dst.signature_entries.extend(src.signature_entries)
    dst.class_hierarchy_entries.extend(src.class_hierarchy_entries)
    dst.interface_hierarchy_entries.extend(src.interface_hierarchy_entries)
    dst.interface_implementation_entries.extend(src.interface_implementation_entries)


def _accumulate_declarations(declared: Dict, src: FileProcessingResult) -> None:
    declared['namespaces'].update(src.declared_namespaces)
    for key, attr in (
        ('interfaces', 'declared_interfaces'),
        ('classes', 'declared_classes'),
        ('structs', 'declared_structs'),
        ('enums', 'declared_enums'),
        ('methods', 'declared_methods'),
        ('properties', 'declared_properties'),
        ('events', 'declared_events'),
        ('constructors', 'declared_constructors'),
    ):
        for name, locations in getattr(src, attr).items():
            declared[key][name].update(locations)


def main() -> int:
    sys.setrecursionlimit(10000)

    print("Mod Code Indexer (incremental)")
    print("=" * 50)
    print(f"Output: {CODE_INDEX_DIR}")
    print()

    run = ModIndexRun()
    run.load_inventory()
    run.hash_mods()
    run.load_old_hashes()
    run.diff_mods()

    parsed = run.parse_changed()
    run.write_index(parsed)

    print("\nIndexing complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
