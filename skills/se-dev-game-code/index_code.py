#!/usr/bin/env python3
"""
C# Codebase Indexer

This script recursively indexes C# source files in a directory structure, creating CSV files
with declarations and usages of namespaces, interfaces, classes, methods, and member variables.

Usage:
    python index_code.py <source_root_path> <output_directory>
"""

import csv
import os
import random
import sys
from dataclasses import dataclass, field
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from tree_sitter import Language, Parser, Node
from tree_sitter_c_sharp import language


@dataclass
class IndexEntry:
    """Represents a single index entry for declarations or usages"""
    namespace: str
    declaring_type: str
    method: str
    variable_name: str
    entry_type: str  # 'declaration' or 'usage'
    file_path: str
    start_line: int
    end_line: int
    description: str

    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format"""
        return [
            self.namespace,
            self.declaring_type,
            self.method,
            self.variable_name,
            self.entry_type,
            self.file_path,
            str(self.start_line),
            str(self.end_line),
            self.description
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            'namespace',
            'declaring_type',
            'method',
            'variable_name',
            'type',
            'file_path',
            'start_line',
            'end_line',
            'description'
        ]


@dataclass
class FileProcessingResult:
    """Results from processing a single file"""
    namespace_entries: List[IndexEntry] = field(default_factory=list)
    interface_entries: List[IndexEntry] = field(default_factory=list)
    class_entries: List[IndexEntry] = field(default_factory=list)
    struct_entries: List[IndexEntry] = field(default_factory=list)
    enum_entries: List[IndexEntry] = field(default_factory=list)
    method_entries: List[IndexEntry] = field(default_factory=list)
    variable_entries: List[IndexEntry] = field(default_factory=list)

    # Declared names found in this file (for building shared state after pass 1)
    declared_namespaces: Set[str] = field(default_factory=set)
    declared_interfaces: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_classes: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_structs: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_enums: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_methods: Dict[str, Set[tuple]] = field(default_factory=dict)


def _process_batch_worker(args: Tuple) -> List[FileProcessingResult]:
    """Worker function to process a batch of files in a subprocess"""
    file_paths, root_path, collect_usages, shared_declarations = args

    # Increase recursion limit for deeply nested code (default is 1000)
    sys.setrecursionlimit(10000)

    processor = FileProcessor(root_path)

    if collect_usages and shared_declarations:
        # Pass 2: use shared declarations
        processor.declared_namespaces = shared_declarations['namespaces']
        processor.declared_interfaces = shared_declarations['interfaces']
        processor.declared_classes = shared_declarations['classes']
        processor.declared_structs = shared_declarations['structs']
        processor.declared_enums = shared_declarations['enums']
        processor.declared_methods = shared_declarations['methods']

    results = []
    for file_path in file_paths:
        try:
            results.append(processor.process_file(file_path, collect_usages))
        except Exception as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            results.append(FileProcessingResult())
    return results


class FileProcessor:
    """Processes a single C# file - designed to be used in worker processes"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.parser = Parser()
        self.parser.language = Language(language())

        # Track declared names for each category to detect usages
        self.declared_namespaces: Set[str] = set()
        self.declared_interfaces: Dict[str, Set[tuple]] = {}
        self.declared_classes: Dict[str, Set[tuple]] = {}
        self.declared_structs: Dict[str, Set[tuple]] = {}
        self.declared_enums: Dict[str, Set[tuple]] = {}
        self.declared_methods: Dict[str, Set[tuple]] = {}

    def process_file(self, file_path: Path, collect_usages: bool) -> FileProcessingResult:
        """Process a single C# file and return results"""
        result = FileProcessingResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                source_code = f.read()

        tree = self.parser.parse(bytes(source_code, 'utf-8'))
        relative_path = str(file_path.relative_to(self.root_path))

        source_lines = source_code.split('\n')

        context = {
            'namespace': '',
            'declaring_type': '',
            'method': '',
            'file_path': relative_path,
            'source_lines': source_lines,
            'collect_usages': collect_usages,
            'result': result
        }

        self._traverse_tree(tree.root_node, context)
        return result

    def _traverse_tree(self, node: Node, context: Dict):
        """Recursively traverse the syntax tree"""
        prev_namespace = context['namespace']
        prev_declaring_type = context['declaring_type']
        prev_method = context['method']
        is_file_scoped_namespace = False
        result = context['result']

        if context['collect_usages']:
            if node.type == 'file_scoped_namespace_declaration':
                name = self._get_identifier_name(node)
                if name:
                    context['namespace'] = name
                    is_file_scoped_namespace = True
            elif node.type == 'namespace_declaration':
                name = self._get_identifier_name(node)
                if name:
                    context['namespace'] = self._build_namespace(context['namespace'], name)
            elif node.type in ('interface_declaration', 'class_declaration', 'struct_declaration',
                             'record_declaration', 'enum_declaration'):
                name = self._get_identifier_name(node)
                if name:
                    context['declaring_type'] = name
            elif node.type in ('method_declaration', 'constructor_declaration'):
                name = self._get_identifier_name(node)
                if name:
                    context['method'] = name
            elif node.type == 'identifier':
                self._process_identifier_usage(node, context, result)
        else:
            if node.type == 'file_scoped_namespace_declaration':
                self._process_file_scoped_namespace(node, context, result)
                is_file_scoped_namespace = True
            elif node.type == 'namespace_declaration':
                self._process_namespace(node, context, result)
            elif node.type == 'interface_declaration':
                self._process_interface(node, context, result)
            elif node.type == 'class_declaration':
                self._process_class(node, context, result)
            elif node.type == 'struct_declaration':
                self._process_struct(node, context, result)
            elif node.type == 'enum_declaration':
                self._process_enum(node, context, result)
            elif node.type == 'record_declaration':
                self._process_class(node, context, result)
            elif node.type in ('method_declaration', 'constructor_declaration'):
                self._process_method(node, context, result)
            elif node.type == 'field_declaration':
                self._process_field(node, context, result)
            elif node.type == 'property_declaration':
                self._process_property(node, context, result)

        for child in node.children:
            self._traverse_tree(child, context)

        if not is_file_scoped_namespace:
            context['namespace'] = prev_namespace
        context['declaring_type'] = prev_declaring_type
        context['method'] = prev_method

    def _get_identifier_name(self, node: Node) -> Optional[str]:
        """Extract identifier name from a node"""
        for child in node.children:
            if child.type == 'identifier':
                return child.text.decode('utf-8')
            elif child.type == 'qualified_name':
                return child.text.decode('utf-8')
        return None

    def _build_namespace(self, current: str, new: str) -> str:
        """Build namespace by concatenating"""
        if current:
            return f"{current}.{new}"
        return new

    def _get_preceding_comment(self, node: Node, source_lines: List[str]) -> str:
        """Extract comment immediately preceding a declaration"""
        start_line = node.start_point[0]

        if start_line == 0:
            return ''

        comment_lines = []
        current_line = start_line - 1

        while current_line >= 0:
            line = source_lines[current_line].strip()

            if line.startswith('//'):
                comment_lines.insert(0, line[2:].strip())
                current_line -= 1
            elif line.endswith('*/'):
                multi_line_parts = []
                while current_line >= 0:
                    line = source_lines[current_line].strip()
                    line = line.replace('/*', '').replace('*/', '').replace('*', '').strip()
                    if line:
                        multi_line_parts.insert(0, line)
                    if '/*' in source_lines[current_line]:
                        break
                    current_line -= 1
                comment_lines = multi_line_parts + comment_lines
                break
            elif not line:
                break
            else:
                break

        return ' '.join(comment_lines)

    def _process_file_scoped_namespace(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process file-scoped namespace declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context['namespace'] = name
        result.declared_namespaces.add(name)

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=name,
            declaring_type='',
            method='',
            variable_name='',
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.namespace_entries.append(entry)

    def _process_namespace(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process namespace declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        full_namespace = self._build_namespace(context['namespace'], name)
        context['namespace'] = full_namespace
        result.declared_namespaces.add(full_namespace)

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=full_namespace,
            declaring_type='',
            method='',
            variable_name='',
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.namespace_entries.append(entry)

    def _process_interface(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process interface declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_interfaces:
            result.declared_interfaces[name] = set()
        result.declared_interfaces[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'],
            declaring_type=name,
            method='',
            variable_name='',
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.interface_entries.append(entry)

    def _process_class(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process class/record declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_classes:
            result.declared_classes[name] = set()
        result.declared_classes[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'],
            declaring_type=name,
            method='',
            variable_name='',
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.class_entries.append(entry)

    def _process_struct(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process struct declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_structs:
            result.declared_structs[name] = set()
        result.declared_structs[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'],
            declaring_type=name,
            method='',
            variable_name='',
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.struct_entries.append(entry)

    def _process_enum(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process enum declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_enums:
            result.declared_enums[name] = set()
        result.declared_enums[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'],
            declaring_type=name,
            method='',
            variable_name='',
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.enum_entries.append(entry)

    def _process_method(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process method or constructor declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context['method'] = name

        if name not in result.declared_methods:
            result.declared_methods[name] = set()
        result.declared_methods[name].add((context['namespace'], context['declaring_type']))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'],
            declaring_type=context['declaring_type'],
            method=name,
            variable_name='',
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.method_entries.append(entry)

    def _process_field(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process field (member variable) declaration"""
        for child in node.children:
            if child.type == 'variable_declaration':
                for declarator in child.children:
                    if declarator.type == 'variable_declarator':
                        name = self._get_identifier_name(declarator)
                        if name:
                            description = self._get_preceding_comment(node, context['source_lines'])

                            entry = IndexEntry(
                                namespace=context['namespace'],
                                declaring_type=context['declaring_type'],
                                method='',
                                variable_name=name,
                                entry_type='declaration',
                                file_path=context['file_path'],
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                description=description
                            )
                            result.variable_entries.append(entry)

    def _process_property(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process property declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'],
            declaring_type=context['declaring_type'],
            method='',
            variable_name=name,
            entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description
        )
        result.variable_entries.append(entry)

    def _process_identifier_usage(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process identifier usage (not a declaration)"""
        parent = node.parent
        if not parent:
            return

        declaration_types = {
            'namespace_declaration',
            'interface_declaration',
            'class_declaration',
            'struct_declaration',
            'record_declaration',
            'enum_declaration',
            'method_declaration',
            'constructor_declaration',
            'field_declaration',
            'property_declaration',
            'variable_declaration',
            'variable_declarator',
            'parameter',
            'type_parameter',
            'using_directive',
            'qualified_name',
            'member_access_expression'
        }

        if parent.type in declaration_types:
            return

        grandparent = parent.parent
        if grandparent and grandparent.type in declaration_types:
            return

        name = node.text.decode('utf-8')
        added = False

        if name in self.declared_namespaces:
            entry = IndexEntry(
                namespace=name,
                declaring_type='',
                method='',
                variable_name='',
                entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=''
            )
            result.namespace_entries.append(entry)
            added = True

        if name in self.declared_interfaces:
            entry = IndexEntry(
                namespace=context['namespace'],
                declaring_type=name,
                method=context['method'],
                variable_name='',
                entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=''
            )
            result.interface_entries.append(entry)
            added = True

        if name in self.declared_classes:
            entry = IndexEntry(
                namespace=context['namespace'],
                declaring_type=name,
                method=context['method'],
                variable_name='',
                entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=''
            )
            result.class_entries.append(entry)
            added = True

        if name in self.declared_structs:
            entry = IndexEntry(
                namespace=context['namespace'],
                declaring_type=name,
                method=context['method'],
                variable_name='',
                entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=''
            )
            result.struct_entries.append(entry)
            added = True

        if name in self.declared_enums:
            entry = IndexEntry(
                namespace=context['namespace'],
                declaring_type=name,
                method=context['method'],
                variable_name='',
                entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=''
            )
            result.enum_entries.append(entry)
            added = True

        if name in self.declared_methods:
            entry = IndexEntry(
                namespace=context['namespace'],
                declaring_type=context['declaring_type'],
                method=name,
                variable_name='',
                entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=''
            )
            result.method_entries.append(entry)
            added = True

        if not added:
            entry = IndexEntry(
                namespace=context['namespace'],
                declaring_type=context['declaring_type'],
                method=context['method'],
                variable_name=name,
                entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=''
            )
            result.variable_entries.append(entry)


class CSharpIndexer:
    """Indexes C# source code using Tree-sitter with parallel processing"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()

        # Separate indices for each category
        self.namespace_index: List[IndexEntry] = []
        self.interface_index: List[IndexEntry] = []
        self.class_index: List[IndexEntry] = []
        self.struct_index: List[IndexEntry] = []
        self.enum_index: List[IndexEntry] = []
        self.method_index: List[IndexEntry] = []
        self.variable_index: List[IndexEntry] = []

        # Track declared names for each category to detect usages
        self.declared_namespaces: Set[str] = set()
        self.declared_interfaces: Dict[str, Set[tuple]] = {}
        self.declared_classes: Dict[str, Set[tuple]] = {}
        self.declared_structs: Dict[str, Set[tuple]] = {}
        self.declared_enums: Dict[str, Set[tuple]] = {}
        self.declared_methods: Dict[str, Set[tuple]] = {}

        # Number of parallel workers (2x CPU cores)
        self.num_workers = cpu_count() * 2

    @staticmethod
    def _create_batches(files: List[Path], batch_size: int) -> List[List[Path]]:
        """Split files into batches of specified size"""
        batches = []
        for i in range(0, len(files), batch_size):
            batches.append(files[i:i + batch_size])
        return batches

    def _merge_batch_results(self, batch_results: List[List[FileProcessingResult]]):
        """Merge results from batched workers into the main indices"""
        for batch in batch_results:
            for result in batch:
                self.namespace_index.extend(result.namespace_entries)
                self.interface_index.extend(result.interface_entries)
                self.class_index.extend(result.class_entries)
                self.struct_index.extend(result.struct_entries)
                self.enum_index.extend(result.enum_entries)
                self.method_index.extend(result.method_entries)
                self.variable_index.extend(result.variable_entries)

    def _merge_batch_declarations(self, batch_results: List[List[FileProcessingResult]]):
        """Merge declared names from batched pass 1 results"""
        for batch in batch_results:
            for result in batch:
                self.declared_namespaces.update(result.declared_namespaces)

                for name, locations in result.declared_interfaces.items():
                    if name not in self.declared_interfaces:
                        self.declared_interfaces[name] = set()
                    self.declared_interfaces[name].update(locations)

                for name, locations in result.declared_classes.items():
                    if name not in self.declared_classes:
                        self.declared_classes[name] = set()
                    self.declared_classes[name].update(locations)

                for name, locations in result.declared_structs.items():
                    if name not in self.declared_structs:
                        self.declared_structs[name] = set()
                    self.declared_structs[name].update(locations)

                for name, locations in result.declared_enums.items():
                    if name not in self.declared_enums:
                        self.declared_enums[name] = set()
                    self.declared_enums[name].update(locations)

                for name, locations in result.declared_methods.items():
                    if name not in self.declared_methods:
                        self.declared_methods[name] = set()
                    self.declared_methods[name].update(locations)

    def index_directory(self):
        """Recursively index all C# files in the directory using parallel processing"""
        cs_files = list(self.root_path.rglob('*.cs'))
        total_files = len(cs_files)

        print(f"Found {total_files} C# files to index...")
        print(f"Using {self.num_workers} parallel workers")

        # Randomize file order for better load distribution
        random.shuffle(cs_files)

        # Create batches of 32 files each for more efficient IPC
        batch_size = 32
        batches = self._create_batches(cs_files, batch_size)
        print(f"Processing in {len(batches)} batches of up to {batch_size} files each")

        # First pass: collect all declarations in parallel
        print("\nPass 1: Collecting declarations...")
        root_path_str = str(self.root_path)
        pass1_args = [(batch, root_path_str, False, None) for batch in batches]

        with Pool(processes=self.num_workers) as pool:
            pass1_results = list(pool.imap_unordered(_process_batch_worker, pass1_args))

        # Merge declaration results
        self._merge_batch_results(pass1_results)
        self._merge_batch_declarations(pass1_results)
        print(f"Completed pass 1: {total_files} files.")

        # Build shared declarations dict for pass 2
        shared_declarations = {
            'namespaces': self.declared_namespaces,
            'interfaces': self.declared_interfaces,
            'classes': self.declared_classes,
            'structs': self.declared_structs,
            'enums': self.declared_enums,
            'methods': self.declared_methods
        }

        # Second pass: collect usages in parallel
        print("\nPass 2: Collecting usages...")
        pass2_args = [(batch, root_path_str, True, shared_declarations) for batch in batches]

        with Pool(processes=self.num_workers) as pool:
            pass2_results = list(pool.imap_unordered(_process_batch_worker, pass2_args))

        # Merge usage results
        self._merge_batch_results(pass2_results)
        print(f"Completed pass 2: {total_files} files.")

    def write_indices(self, output_dir: Path):
        """Write all indices to CSV files"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Sort and write each index
        indices = [
            ('namespaces.csv', self.namespace_index),
            ('interfaces.csv', self.interface_index),
            ('classes.csv', self.class_index),
            ('structs.csv', self.struct_index),
            ('enums.csv', self.enum_index),
            ('methods.csv', self.method_index),
            ('variables.csv', self.variable_index)
        ]

        for filename, index_data in indices:
            # Sort by all columns left to right
            sorted_data = sorted(
                index_data,
                key=lambda e: (
                    e.namespace,
                    e.declaring_type,
                    e.method,
                    e.variable_name,
                    e.entry_type,
                    e.file_path,
                    e.start_line,
                    e.end_line
                )
            )

            output_path = output_dir / filename
            print(f"Writing {len(sorted_data)} entries to {output_path}...")

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(IndexEntry.csv_header())
                for entry in sorted_data:
                    writer.writerow(entry.to_csv_row())

        print(f"\nIndex files written to {output_dir}")
        print(f"  - Namespaces: {len(self.namespace_index)} entries")
        print(f"  - Interfaces: {len(self.interface_index)} entries")
        print(f"  - Classes: {len(self.class_index)} entries")
        print(f"  - Structs: {len(self.struct_index)} entries")
        print(f"  - Enums: {len(self.enum_index)} entries")
        print(f"  - Methods: {len(self.method_index)} entries")
        print(f"  - Variables: {len(self.variable_index)} entries")


def main():
    if len(sys.argv) != 3:
        print("Usage: python index_code.py <source_root_path> <output_directory>")
        sys.exit(1)

    source_root = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(source_root):
        print(f"Error: Source path '{source_root}' is not a directory")
        sys.exit(1)

    # Increase recursion limit for deeply nested code (default is 1000)
    sys.setrecursionlimit(10000)

    print(f"Indexing C# codebase at: {source_root}")
    print(f"Output directory: {output_dir}")
    print()

    indexer = CSharpIndexer(source_root)
    indexer.index_directory()
    indexer.write_indices(Path(output_dir))

    print("\nIndexing complete!")


if __name__ == '__main__':
    main()
