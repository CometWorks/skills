#!/usr/bin/env python3
"""
Torch source indexer.

Indexes the C# source files of a Torch checkout into CSV files that can be
searched by search_torch.py.
"""

import csv
import random
import sys
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from cs_indexer import (
    CLASS_HIERARCHY_FILE,
    INDEX_ENTRY_FILES,
    INTERFACE_HIERARCHY_FILE,
    INTERFACE_IMPL_FILE,
    SIGNATURE_FILE,
    ClassHierarchyEntry,
    FileProcessingResult,
    FileProcessor,
    IndexEntry,
    InterfaceHierarchyEntry,
    InterfaceImplementationEntry,
    SignatureEntry,
)
from hierarchy_tree import build_class_tree, build_interface_tree
from torch_paths import CODE_INDEX_DIR, get_torch_root


CATEGORIES = [
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
]

EXCLUDED_DIR_NAMES = frozenset({
    ".git",
    ".vs",
    "bin",
    "obj",
    "packages",
})

BATCH_SIZE = 32


def _collect_source_files(root: Path) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    for cs_file in root.rglob("*.cs"):
        if not cs_file.is_file():
            continue
        if any(part in EXCLUDED_DIR_NAMES for part in cs_file.parts):
            continue
        rel_path = cs_file.relative_to(root).as_posix()
        items.append((str(cs_file), rel_path))
    items.sort(key=lambda item: item[1])
    return items


def _process_batch_worker(args: Tuple) -> List[FileProcessingResult]:
    items, collect_usages, shared_declarations = args

    sys.setrecursionlimit(10000)
    processor = FileProcessor(root_path=".")

    if collect_usages and shared_declarations:
        processor.declared_namespaces = shared_declarations["namespaces"]
        processor.declared_interfaces = shared_declarations["interfaces"]
        processor.declared_classes = shared_declarations["classes"]
        processor.declared_structs = shared_declarations["structs"]
        processor.declared_enums = shared_declarations["enums"]
        processor.declared_methods = shared_declarations["methods"]
        processor.declared_properties = shared_declarations["properties"]
        processor.declared_events = shared_declarations["events"]
        processor.declared_constructors = shared_declarations["constructors"]

    results: List[FileProcessingResult] = []
    for abs_path, path_label in items:
        try:
            results.append(
                processor.process_file(
                    Path(abs_path), collect_usages, path_label=path_label
                )
            )
        except Exception as exc:  # noqa: BLE001
            print(f"Error processing {abs_path}: {exc}", file=sys.stderr)
            results.append(FileProcessingResult())
    return results


def _batch(items: List, size: int) -> List[List]:
    return [items[i : i + size] for i in range(0, len(items), size)]


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
    declared["namespaces"].update(src.declared_namespaces)
    for key, attr in (
        ("interfaces", "declared_interfaces"),
        ("classes", "declared_classes"),
        ("structs", "declared_structs"),
        ("enums", "declared_enums"),
        ("methods", "declared_methods"),
        ("properties", "declared_properties"),
        ("events", "declared_events"),
        ("constructors", "declared_constructors"),
    ):
        for name, locations in getattr(src, attr).items():
            declared[key][name].update(locations)


def _sort_value(value: str):
    if value.isdigit():
        return (0, int(value))
    return (1, value)


class TorchIndexRun:
    def __init__(self, source_root: Path):
        self.source_root = source_root
        self.items: List[Tuple[str, str]] = []
        self.num_workers = max(1, cpu_count() * 2)

    def collect_files(self) -> None:
        self.items = _collect_source_files(self.source_root)
        print(f"Source: {self.source_root}")
        print(f"Files:  {len(self.items)}")

    def parse(self) -> Optional[FileProcessingResult]:
        if not self.items:
            print("No C# source files found.")
            return None

        random.shuffle(self.items)
        batches = _batch(self.items, BATCH_SIZE)

        print(f"Pass 1 (declarations): {len(batches)} batches, {self.num_workers} workers")
        pass1_args = [(batch, False, None) for batch in batches]
        with Pool(processes=self.num_workers) as pool:
            pass1_results = list(pool.imap_unordered(_process_batch_worker, pass1_args))

        merged = FileProcessingResult()
        declared = {
            "namespaces": set(),
            "interfaces": defaultdict(set),
            "classes": defaultdict(set),
            "structs": defaultdict(set),
            "enums": defaultdict(set),
            "methods": defaultdict(set),
            "properties": defaultdict(set),
            "events": defaultdict(set),
            "constructors": defaultdict(set),
        }
        for batch_results in pass1_results:
            for result in batch_results:
                _accumulate_result(merged, result)
                _accumulate_declarations(declared, result)

        shared_declarations = {
            "namespaces": declared["namespaces"],
            "interfaces": dict(declared["interfaces"]),
            "classes": dict(declared["classes"]),
            "structs": dict(declared["structs"]),
            "enums": dict(declared["enums"]),
            "methods": dict(declared["methods"]),
            "properties": dict(declared["properties"]),
            "events": dict(declared["events"]),
            "constructors": dict(declared["constructors"]),
        }

        print(f"Pass 2 (usages): {len(batches)} batches")
        pass2_args = [(batch, True, shared_declarations) for batch in batches]
        with Pool(processes=self.num_workers) as pool:
            pass2_results = list(pool.imap_unordered(_process_batch_worker, pass2_args))

        for batch_results in pass2_results:
            for result in batch_results:
                _accumulate_result(merged, result)

        return merged

    def write_index(self, parsed: Optional[FileProcessingResult]) -> None:
        CODE_INDEX_DIR.mkdir(parents=True, exist_ok=True)

        rows_by_file: Dict[str, List[List[str]]] = defaultdict(list)
        if parsed is not None:
            for category in CATEGORIES:
                entries: List[IndexEntry] = getattr(parsed, f"{category}_entries")
                decls = [entry for entry in entries if entry.entry_type == "declaration"]
                usages = [entry for entry in entries if entry.entry_type == "usage"]
                rows_by_file[f"{category}_declarations.csv"] = [
                    entry.to_csv_row() for entry in decls
                ]
                rows_by_file[f"{category}_usages.csv"] = [
                    entry.to_csv_row() for entry in usages
                ]

            rows_by_file[SIGNATURE_FILE] = [
                entry.to_csv_row() for entry in parsed.signature_entries
            ]
            rows_by_file[CLASS_HIERARCHY_FILE] = [
                entry.to_csv_row() for entry in parsed.class_hierarchy_entries
            ]
            rows_by_file[INTERFACE_HIERARCHY_FILE] = [
                entry.to_csv_row() for entry in parsed.interface_hierarchy_entries
            ]
            rows_by_file[INTERFACE_IMPL_FILE] = [
                entry.to_csv_row() for entry in parsed.interface_implementation_entries
            ]

        headers: Dict[str, List[str]] = {}
        for fname in INDEX_ENTRY_FILES:
            headers[fname] = IndexEntry.csv_header()
        headers[SIGNATURE_FILE] = SignatureEntry.csv_header()
        headers[CLASS_HIERARCHY_FILE] = ClassHierarchyEntry.csv_header()
        headers[INTERFACE_HIERARCHY_FILE] = InterfaceHierarchyEntry.csv_header()
        headers[INTERFACE_IMPL_FILE] = InterfaceImplementationEntry.csv_header()

        sort_keys: Dict[str, List[int]] = {}
        index_entry_sort = [0, 1, 2, 3, 5, 6, 7]
        for fname in INDEX_ENTRY_FILES:
            sort_keys[fname] = index_entry_sort
        sort_keys[SIGNATURE_FILE] = [0, 1, 2, 4, 5, 6]
        sort_keys[CLASS_HIERARCHY_FILE] = [0, 1, 2, 3]
        sort_keys[INTERFACE_HIERARCHY_FILE] = [0, 1, 2, 3]
        sort_keys[INTERFACE_IMPL_FILE] = [0, 1, 2]

        all_files = list(INDEX_ENTRY_FILES) + [
            SIGNATURE_FILE,
            CLASS_HIERARCHY_FILE,
            INTERFACE_HIERARCHY_FILE,
            INTERFACE_IMPL_FILE,
        ]

        totals: Dict[str, int] = {}
        for fname in all_files:
            csv_path = CODE_INDEX_DIR / fname
            rows = rows_by_file.get(fname, [])
            keys = sort_keys[fname]
            rows.sort(
                key=lambda row, key_list=keys: tuple(
                    _sort_value(row[key]) if key < len(row) else "" for key in key_list
                )
            )
            with open(csv_path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerow(headers[fname])
                writer.writerows(rows)
            totals[fname] = len(rows)

        self._write_hierarchy_trees()

        decls = sum(totals.get(f"{category}_declarations.csv", 0) for category in CATEGORIES)
        usages = sum(totals.get(f"{category}_usages.csv", 0) for category in CATEGORIES)
        print(f"\nIndex written to {CODE_INDEX_DIR}")
        print(f"  Declarations: {decls}")
        print(f"  Usages:       {usages}")
        print(f"  Signatures:   {totals.get(SIGNATURE_FILE, 0)}")
        print(f"  Class hier:   {totals.get(CLASS_HIERARCHY_FILE, 0)}")
        print(f"  Iface hier:   {totals.get(INTERFACE_HIERARCHY_FILE, 0)}")
        print(f"  Iface impls:  {totals.get(INTERFACE_IMPL_FILE, 0)}")

    def _write_hierarchy_trees(self) -> None:
        class_rows = _load_csv_rows(CODE_INDEX_DIR / CLASS_HIERARCHY_FILE)
        if class_rows:
            tuples = [(row[0], row[1], row[2], row[3]) for row in class_rows if len(row) >= 4]
            text = build_class_tree(tuples)
            (CODE_INDEX_DIR / "class_hierarchy.txt").write_text(text, encoding="utf-8")

        iface_rows = _load_csv_rows(CODE_INDEX_DIR / INTERFACE_HIERARCHY_FILE)
        if iface_rows:
            tuples = [(row[0], row[1], row[2], row[3]) for row in iface_rows if len(row) >= 4]
            text = build_interface_tree(tuples)
            (CODE_INDEX_DIR / "interface_hierarchy.txt").write_text(text, encoding="utf-8")


def _load_csv_rows(path: Path) -> List[List[str]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return list(reader)


def main() -> int:
    try:
        source_root = get_torch_root()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    sys.setrecursionlimit(10000)

    print("Torch Source Indexer")
    print("=" * 50)
    run = TorchIndexRun(source_root)
    run.collect_files()
    parsed = run.parse()
    run.write_index(parsed)
    print("\nIndexing complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
