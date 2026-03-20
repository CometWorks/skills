#!/usr/bin/env python3
"""
PB Script Code Indexer

This script indexes C# source files from Steam and local PB scripts, creating CSV files
with declarations and usages of namespaces, interfaces, classes, methods, and member variables.

Usage:
    python index_scripts.py

The script searches for scripts in:
- SteamScripts/ - Downloaded scripts from Steam Workshop (folders with Script.cs file)
- LocalScripts/ - Local development scripts

Output is written to ScriptCodeIndex/ directory.
"""

import csv
import json
import random
import re
import sys
from dataclasses import dataclass, field
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from tree_sitter import Language, Parser, Node
from tree_sitter_c_sharp import language

SCRIPT_DIR = Path(__file__).parent.resolve()
STEAM_SCRIPTS_DIR = SCRIPT_DIR / "SteamScripts"
LOCAL_SCRIPTS_DIR = SCRIPT_DIR / "LocalScripts"
OUTPUT_DIR = SCRIPT_DIR / "ScriptCodeIndex"
SCRIPT_LIST_FILE = OUTPUT_DIR / "scripts.json"


@dataclass
class IndexEntry:
    """Represents a single index entry for declarations or usages"""
    namespace: str
    declaring_type: str
    method: str
    symbol_name: str
    entry_type: str  # 'declaration' or 'usage'
    file_path: str
    start_line: int
    end_line: int
    description: str
    access: str = ""  # Access modifier: public, private, protected, internal, protected internal
    modifiers: str = ""  # Other modifiers: static, readonly, const, virtual, override, etc. (space-separated)
    member_type: str = ""  # C# type: int, string, List<int>, void, etc.
    params: str = ""  # Parameter list for methods/constructors: (int x, string name)

    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format"""
        return [
            self.namespace,
            self.declaring_type,
            self.method,
            self.symbol_name,
            self.entry_type,
            self.file_path,
            str(self.start_line),
            str(self.end_line),
            self.description,
            self.access,
            self.modifiers,
            self.member_type,
            self.params,
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            'namespace',
            'declaring_type',
            'method',
            'symbol_name',
            'type',
            'file_path',
            'start_line',
            'end_line',
            'description',
            'access',
            'modifiers',
            'member_type',
            'params',
        ]


@dataclass
class SignatureEntry:
    """Represents a method signature entry - different columns than IndexEntry"""
    namespace: str
    declaring_type: str
    method_name: str
    signature: str
    file_path: str
    start_line: int
    end_line: int
    description: str

    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format"""
        return [
            self.namespace,
            self.declaring_type,
            self.method_name,
            self.signature,
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
            'method_name',
            'signature',
            'file_path',
            'start_line',
            'end_line',
            'description'
        ]


@dataclass
class ClassHierarchyEntry:
    """Represents a class inheritance relationship"""
    child_namespace: str
    child_class: str
    parent_namespace: str
    parent_class: str
    file_path: str
    start_line: int
    end_line: int

    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format"""
        return [
            self.child_namespace,
            self.child_class,
            self.parent_namespace,
            self.parent_class,
            self.file_path,
            str(self.start_line),
            str(self.end_line)
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            'child_namespace',
            'child_class',
            'parent_namespace',
            'parent_class',
            'file_path',
            'start_line',
            'end_line'
        ]


@dataclass
class InterfaceHierarchyEntry:
    """Represents an interface inheritance relationship"""
    child_namespace: str
    child_interface: str
    parent_namespace: str
    parent_interface: str
    file_path: str
    start_line: int
    end_line: int

    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format"""
        return [
            self.child_namespace,
            self.child_interface,
            self.parent_namespace,
            self.parent_interface,
            self.file_path,
            str(self.start_line),
            str(self.end_line)
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            'child_namespace',
            'child_interface',
            'parent_namespace',
            'parent_interface',
            'file_path',
            'start_line',
            'end_line'
        ]


@dataclass
class InterfaceImplementationEntry:
    """Represents a class/struct implementing interfaces"""
    implementing_namespace: str
    implementing_type: str
    interfaces: str  # Comma-separated list of fully-qualified interface names
    file_path: str
    start_line: int
    end_line: int

    def to_csv_row(self) -> List[str]:
        """Convert to CSV row format"""
        return [
            self.implementing_namespace,
            self.implementing_type,
            self.interfaces,
            self.file_path,
            str(self.start_line),
            str(self.end_line)
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            'implementing_namespace',
            'implementing_type',
            'interfaces',
            'file_path',
            'start_line',
            'end_line'
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
    field_entries: List[IndexEntry] = field(default_factory=list)
    property_entries: List[IndexEntry] = field(default_factory=list)
    event_entries: List[IndexEntry] = field(default_factory=list)
    constructor_entries: List[IndexEntry] = field(default_factory=list)
    signature_entries: List[SignatureEntry] = field(default_factory=list)

    # Hierarchy entries
    class_hierarchy_entries: List[ClassHierarchyEntry] = field(default_factory=list)
    interface_hierarchy_entries: List[InterfaceHierarchyEntry] = field(default_factory=list)
    interface_implementation_entries: List[InterfaceImplementationEntry] = field(default_factory=list)

    # Declared names found in this file (for building shared state after pass 1)
    declared_namespaces: Set[str] = field(default_factory=set)
    declared_interfaces: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_classes: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_structs: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_enums: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_methods: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_properties: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_events: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_constructors: Dict[str, Set[tuple]] = field(default_factory=dict)


def _process_batch_worker(args: Tuple) -> List[FileProcessingResult]:
    """Worker function to process a batch of files in a subprocess"""
    file_paths, root_path, collect_usages, shared_declarations = args

    sys.setrecursionlimit(10000)

    processor = FileProcessor(root_path)

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

        self.declared_namespaces: Set[str] = set()
        self.declared_interfaces: Dict[str, Set[tuple]] = {}
        self.declared_classes: Dict[str, Set[tuple]] = {}
        self.declared_structs: Dict[str, Set[tuple]] = {}
        self.declared_enums: Dict[str, Set[tuple]] = {}
        self.declared_methods: Dict[str, Set[tuple]] = {}
        self.declared_properties: Dict[str, Set[tuple]] = {}
        self.declared_events: Dict[str, Set[tuple]] = {}
        self.declared_constructors: Dict[str, Set[tuple]] = {}

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
                # Process hierarchy/implementation in Pass 2 where
                # declared_interfaces is populated from all files
                if node.type != 'enum_declaration':
                    self._process_type_hierarchy(node, context, result)
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
            elif node.type in ('event_field_declaration', 'event_declaration'):
                self._process_event(node, context, result)

        for child in node.children:
            self._traverse_tree(child, context)

        if not is_file_scoped_namespace:
            context['namespace'] = prev_namespace
        context['declaring_type'] = prev_declaring_type
        context['method'] = prev_method

    def _get_identifier_name(self, node: Node) -> Optional[str]:
        """Extract identifier name from a node"""
        if node.type in ('method_declaration', 'constructor_declaration'):
            identifiers = []
            for child in node.children:
                if child.type == 'identifier':
                    identifiers.append(child.text.decode('utf-8'))
                elif child.type == 'parameter_list' and identifiers:
                    return identifiers[-1]
            if identifiers:
                return identifiers[-1]
        else:
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf-8')
                elif child.type == 'qualified_name':
                    return child.text.decode('utf-8')
        return None

    def _build_namespace(self, current: str, new: str) -> str:
        if current:
            return f"{current}.{new}"
        return new

    def _get_preceding_comment(self, node: Node, source_lines: List[str]) -> str:
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

    # Access modifier keywords recognized by C#
    _ACCESS_KEYWORDS = frozenset({"public", "private", "protected", "internal"})

    # Other modifier keywords (non-access)
    _MODIFIER_KEYWORDS = frozenset(
        {
            "static",
            "readonly",
            "const",
            "volatile",
            "virtual",
            "override",
            "abstract",
            "sealed",
            "async",
            "extern",
            "new",
            "unsafe",
            "partial",
        }
    )

    def _extract_modifiers(self, node: Node) -> tuple:
        """
        Extract access and other modifiers from a declaration node.
        Returns (access: str, modifiers: str).

        Access is a single string like 'public', 'private', 'protected internal'.
        Modifiers is a space-separated string of non-access modifiers like 'static readonly'.
        """
        access_parts = []
        modifier_parts = []
        for child in node.children:
            if child.type == "modifier":
                for kw in child.children:
                    keyword = kw.type
                    if keyword in self._ACCESS_KEYWORDS:
                        access_parts.append(keyword)
                    elif keyword in self._MODIFIER_KEYWORDS:
                        modifier_parts.append(keyword)
        return (" ".join(access_parts), " ".join(modifier_parts))

    @staticmethod
    def _extract_full_type_text(type_node: Node) -> str:
        """
        Extract the full text of a C# type node, preserving generics.
        E.g. 'List<int>', 'Dictionary<string, List<int>>', 'int', 'void'.
        """
        if type_node is None:
            return ""
        text = type_node.text
        if text:
            return text.decode("utf-8")
        return ""

    @staticmethod
    def _extract_params_text(node: Node) -> str:
        """
        Extract the full parameter list text from a method/constructor node.
        Returns the text including parentheses, e.g. '(int x, string name)'.
        """
        for child in node.children:
            if child.type == "parameter_list":
                text = child.text
                if text:
                    raw = text.decode("utf-8")
                    return re.sub(r"\s+", " ", raw).strip()
        return ""

    def _extract_type_name(self, node: Node) -> Optional[str]:
        if node.type == 'identifier':
            text = node.text
            if text:
                return text.decode('utf-8')
        elif node.type == 'qualified_name':
            text = node.text
            if text:
                return text.decode('utf-8')
        elif node.type == 'generic_name':
            for child in node.children:
                if child.type == 'identifier':
                    text = child.text
                    if text:
                        return text.decode('utf-8')
        return None

    def _get_base_list_types(self, node: Node) -> List[str]:
        types = []
        for child in node.children:
            if child.type in ('identifier', 'qualified_name', 'generic_name'):
                type_name = self._extract_type_name(child)
                if type_name:
                    types.append(type_name)
        return types

    def _find_base_list(self, node: Node) -> Optional[Node]:
        for child in node.children:
            if child.type == 'base_list':
                return child
        return None

    def _resolve_type_namespace(self, type_name: str, current_namespace: str) -> str:
        if '.' in type_name:
            return type_name

        full_name = f"{current_namespace}.{type_name}" if current_namespace else type_name

        if type_name in self.declared_interfaces:
            locations = self.declared_interfaces[type_name]
            for ns, _ in locations:
                if ns == current_namespace:
                    return full_name
            if locations:
                ns, _ = next(iter(locations))
                return f"{ns}.{type_name}" if ns else type_name

        if type_name in self.declared_classes:
            locations = self.declared_classes[type_name]
            for ns, _ in locations:
                if ns == current_namespace:
                    return full_name
            if locations:
                ns, _ = next(iter(locations))
                return f"{ns}.{type_name}" if ns else type_name

        if type_name in self.declared_structs:
            locations = self.declared_structs[type_name]
            for ns, _ in locations:
                if ns == current_namespace:
                    return full_name
            if locations:
                ns, _ = next(iter(locations))
                return f"{ns}.{type_name}" if ns else type_name

        return full_name

    def _split_namespace_and_type(self, fully_qualified: str) -> Tuple[str, str]:
        if '.' not in fully_qualified:
            return ('', fully_qualified)
        parts = fully_qualified.rsplit('.', 1)
        return (parts[0], parts[1])

    def _extract_method_signature(self, node: Node, source_lines: List[str]) -> Tuple[str, int, int]:
        start_line = node.start_point[0]
        start_col = node.start_point[1]

        body_node = None
        semicolon_pos = None
        for child in node.children:
            if child.type == 'block':
                body_node = child
                break
            elif child.type == 'arrow_expression_clause':
                body_node = child
                break
            elif child.type == ';':
                semicolon_pos = (child.start_point[0], child.start_point[1])

        if body_node:
            end_line = body_node.start_point[0]
            end_col = body_node.start_point[1]
        elif semicolon_pos:
            end_line = semicolon_pos[0]
            end_col = semicolon_pos[1] + 1
        else:
            end_line = start_line
            end_col = len(source_lines[start_line]) if start_line < len(source_lines) else 0

        sig_parts = []
        for line_idx in range(start_line, end_line + 1):
            if line_idx >= len(source_lines):
                break
            line = source_lines[line_idx]
            if line_idx == start_line and line_idx == end_line:
                sig_parts.append(line[start_col:end_col])
            elif line_idx == start_line:
                sig_parts.append(line[start_col:])
            elif line_idx == end_line:
                sig_parts.append(line[:end_col])
            else:
                sig_parts.append(line)

        raw_signature = ' '.join(sig_parts)
        normalized = re.sub(r'\s+', ' ', raw_signature).strip()

        if end_line > start_line:
            sig_end_line = end_line
        else:
            sig_end_line = end_line + 1

        return (normalized, start_line + 1, sig_end_line)

    def _process_file_scoped_namespace(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        context['namespace'] = name
        result.declared_namespaces.add(name)

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=name, declaring_type='', method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description
        )
        result.namespace_entries.append(entry)

    def _process_namespace(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        full_namespace = self._build_namespace(context['namespace'], name)
        context['namespace'] = full_namespace
        result.declared_namespaces.add(full_namespace)

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=full_namespace, declaring_type='', method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description
        )
        result.namespace_entries.append(entry)

    def _process_interface(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_interfaces:
            result.declared_interfaces[name] = set()
        result.declared_interfaces[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description
        )
        result.interface_entries.append(entry)

        # Note: interface hierarchy extraction is done in Pass 2
        # (_process_type_hierarchy) where declared_interfaces is populated

    def _process_type_hierarchy(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process base types for class/struct/record/interface declarations.

        Called during Pass 2 when self.declared_interfaces is populated
        with all interface declarations from the entire codebase.
        """
        name = self._get_identifier_name(node)
        if not name:
            return

        base_list = self._find_base_list(node)
        if not base_list:
            return

        base_types = self._get_base_list_types(base_list)
        if not base_types:
            return

        if node.type == 'interface_declaration':
            # All items in interface base list are parent interfaces
            for parent_type in base_types:
                parent_fqn = self._resolve_type_namespace(parent_type, context['namespace'])
                parent_ns, parent_name = self._split_namespace_and_type(parent_fqn)

                hier_entry = InterfaceHierarchyEntry(
                    child_namespace=context['namespace'], child_interface=name,
                    parent_namespace=parent_ns, parent_interface=parent_name,
                    file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1
                )
                result.interface_hierarchy_entries.append(hier_entry)

        elif node.type == 'struct_declaration':
            # Structs can only implement interfaces (no struct inheritance)
            interface_fqns = []
            for iface in base_types:
                iface_fqn = self._resolve_type_namespace(iface, context['namespace'])
                interface_fqns.append(iface_fqn)

            impl_entry = InterfaceImplementationEntry(
                implementing_namespace=context['namespace'], implementing_type=name,
                interfaces=','.join(interface_fqns), file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1
            )
            result.interface_implementation_entries.append(impl_entry)

        else:
            # class_declaration or record_declaration
            # First item could be base class or interface
            first_type = base_types[0]
            first_fqn = self._resolve_type_namespace(first_type, context['namespace'])
            first_ns, first_name = self._split_namespace_and_type(first_fqn)

            # Check if first type is an interface (declared_interfaces is
            # populated from Pass 1, so this check is now reliable)
            is_interface = first_name in self.declared_interfaces

            interfaces = []
            if is_interface:
                # All items are interfaces
                interfaces = base_types
            else:
                # First item is base class, rest are interfaces
                hier_entry = ClassHierarchyEntry(
                    child_namespace=context['namespace'], child_class=name,
                    parent_namespace=first_ns, parent_class=first_name,
                    file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1
                )
                result.class_hierarchy_entries.append(hier_entry)
                interfaces = base_types[1:]

            # Process interfaces
            if interfaces:
                interface_fqns = []
                for iface in interfaces:
                    iface_fqn = self._resolve_type_namespace(iface, context['namespace'])
                    interface_fqns.append(iface_fqn)

                impl_entry = InterfaceImplementationEntry(
                    implementing_namespace=context['namespace'], implementing_type=name,
                    interfaces=','.join(interface_fqns), file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1
                )
                result.interface_implementation_entries.append(impl_entry)

    def _process_class(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_classes:
            result.declared_classes[name] = set()
        result.declared_classes[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description
        )
        result.class_entries.append(entry)

        # Note: hierarchy/implementation extraction is done in Pass 2
        # (_process_type_hierarchy) where declared_interfaces is populated

    def _process_struct(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_structs:
            result.declared_structs[name] = set()
        result.declared_structs[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description
        )
        result.struct_entries.append(entry)

        # Note: interface implementation extraction is done in Pass 2
        # (_process_type_hierarchy) where declared_interfaces is populated

    def _process_enum(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        context['declaring_type'] = name

        if name not in result.declared_enums:
            result.declared_enums[name] = set()
        result.declared_enums[name].add((context['namespace'], ''))

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description
        )
        result.enum_entries.append(entry)

    def _process_method(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        is_constructor = node.type == "constructor_declaration"

        context['method'] = name

        if name not in result.declared_methods:
            result.declared_methods[name] = set()
        result.declared_methods[name].add((context['namespace'], context['declaring_type']))

        if is_constructor:
            if name not in result.declared_constructors:
                result.declared_constructors[name] = set()
            result.declared_constructors[name].add((context['namespace'], context['declaring_type']))

        access, modifiers = self._extract_modifiers(node)
        params_text = self._extract_params_text(node)

        # Extract return type (methods only — constructors have no return type)
        return_type = ""
        if not is_constructor:
            found_type = False
            for child in node.children:
                if child.type == "modifier":
                    continue
                if not found_type and child.type != "identifier":
                    return_type = self._extract_full_type_text(child)
                    found_type = True
                elif child.type == "identifier":
                    break

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'], declaring_type=context['declaring_type'],
            method=name, symbol_name='', entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description,
            access=access, modifiers=modifiers, member_type=return_type, params=params_text,
        )

        if is_constructor:
            result.constructor_entries.append(entry)
        else:
            result.method_entries.append(entry)

        signature_text, sig_start, sig_end = self._extract_method_signature(node, context['source_lines'])
        sig_entry = SignatureEntry(
            namespace=context['namespace'], declaring_type=context['declaring_type'],
            method_name=name, signature=signature_text, file_path=context['file_path'],
            start_line=sig_start, end_line=sig_end, description=description
        )
        result.signature_entries.append(sig_entry)

    def _process_field(self, node: Node, context: Dict, result: FileProcessingResult):
        access, modifiers = self._extract_modifiers(node)

        for child in node.children:
            if child.type == 'variable_declaration':
                # Extract the type from the variable_declaration
                type_text = ""
                for vc in child.children:
                    if vc.type not in ("variable_declarator", ",", ";"):
                        type_text = self._extract_full_type_text(vc)
                        break
                for declarator in child.children:
                    if declarator.type == 'variable_declarator':
                        name = self._get_identifier_name(declarator)
                        if name:
                            description = self._get_preceding_comment(node, context['source_lines'])
                            entry = IndexEntry(
                                namespace=context['namespace'], declaring_type=context['declaring_type'],
                                method='', symbol_name=name, entry_type='declaration',
                                file_path=context['file_path'],
                                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                                description=description,
                                access=access, modifiers=modifiers, member_type=type_text,
                            )
                            result.field_entries.append(entry)

    def _process_property(self, node: Node, context: Dict, result: FileProcessingResult):
        name = self._get_identifier_name(node)
        if not name:
            return

        if name not in result.declared_properties:
            result.declared_properties[name] = set()
        result.declared_properties[name].add((context['namespace'], context['declaring_type']))

        access, modifiers = self._extract_modifiers(node)

        # Property type is a direct child with field name [type]
        type_text = ""
        for child in node.children:
            if child.type not in (
                "modifier", "identifier", "accessor_list",
                "arrow_expression_clause", "=", ";", "{", "}",
            ):
                type_text = self._extract_full_type_text(child)
                break

        description = self._get_preceding_comment(node, context['source_lines'])

        entry = IndexEntry(
            namespace=context['namespace'], declaring_type=context['declaring_type'],
            method='', symbol_name=name, entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=description,
            access=access, modifiers=modifiers, member_type=type_text,
        )
        result.property_entries.append(entry)

    def _process_event(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process event declaration (event_field_declaration or event_declaration)"""
        access, modifiers = self._extract_modifiers(node)

        if node.type == "event_field_declaration":
            # event_field_declaration has: modifier* event variable_declaration ;
            for child in node.children:
                if child.type == "variable_declaration":
                    type_text = ""
                    for vc in child.children:
                        if vc.type not in ("variable_declarator", ",", ";"):
                            type_text = self._extract_full_type_text(vc)
                    for vc in child.children:
                        if vc.type == "variable_declarator":
                            name = self._get_identifier_name(vc)
                            if name:
                                if name not in result.declared_events:
                                    result.declared_events[name] = set()
                                result.declared_events[name].add(
                                    (context['namespace'], context['declaring_type'])
                                )
                                description = self._get_preceding_comment(node, context['source_lines'])
                                entry = IndexEntry(
                                    namespace=context['namespace'],
                                    declaring_type=context['declaring_type'],
                                    method='', symbol_name=name,
                                    entry_type='declaration',
                                    file_path=context['file_path'],
                                    start_line=node.start_point[0] + 1,
                                    end_line=node.end_point[0] + 1,
                                    description=description,
                                    access=access, modifiers=modifiers, member_type=type_text,
                                )
                                result.event_entries.append(entry)
        else:
            # event_declaration has: modifier* event type name accessor_list
            name = self._get_identifier_name(node)
            if not name:
                return

            if name not in result.declared_events:
                result.declared_events[name] = set()
            result.declared_events[name].add(
                (context['namespace'], context['declaring_type'])
            )

            # Find the type node (comes after 'event' keyword, before the identifier)
            type_text = ""
            found_event_keyword = False
            for child in node.children:
                if child.type == "event":
                    found_event_keyword = True
                elif (
                    found_event_keyword
                    and child.type != "identifier"
                    and child.type != "accessor_list"
                    and child.type != ";"
                ):
                    type_text = self._extract_full_type_text(child)
                    break
            description = self._get_preceding_comment(node, context['source_lines'])
            entry = IndexEntry(
                namespace=context['namespace'],
                declaring_type=context['declaring_type'],
                method='', symbol_name=name,
                entry_type='declaration',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=description,
                access=access, modifiers=modifiers, member_type=type_text,
            )
            result.event_entries.append(entry)

    def _process_identifier_usage(self, node: Node, context: Dict, result: FileProcessingResult):
        parent = node.parent
        if not parent:
            return

        declaration_types = {
            'namespace_declaration', 'interface_declaration', 'class_declaration',
            'struct_declaration', 'record_declaration', 'enum_declaration',
            'method_declaration', 'constructor_declaration', 'field_declaration',
            'property_declaration', 'variable_declaration', 'variable_declarator',
            'parameter', 'type_parameter', 'using_directive', 'qualified_name',
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
                namespace=name, declaring_type='', method='', symbol_name='',
                entry_type='usage', file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.namespace_entries.append(entry)
            added = True

        if name in self.declared_interfaces:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.interface_entries.append(entry)
            added = True

        if name in self.declared_classes:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.class_entries.append(entry)
            added = True

        if name in self.declared_structs:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.struct_entries.append(entry)
            added = True

        if name in self.declared_enums:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.enum_entries.append(entry)
            added = True

        if name in self.declared_methods:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=name, symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.method_entries.append(entry)
            added = True

        # Constructor usage: identifier inside object_creation_expression (new Foo())
        if name in self.declared_constructors:
            is_constructor_usage = False
            p = parent
            while p:
                if p.type == "object_creation_expression":
                    is_constructor_usage = True
                    break
                if p.type in ("argument_list", "qualified_name"):
                    p = p.parent
                else:
                    break
            if is_constructor_usage:
                entry = IndexEntry(
                    namespace=context['namespace'], declaring_type=context['declaring_type'],
                    method=name, symbol_name='', entry_type='usage',
                    file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                    description=''
                )
                result.constructor_entries.append(entry)
                added = True

        if name in self.declared_properties:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=context['method'], symbol_name=name, entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.property_entries.append(entry)
            added = True

        if name in self.declared_events:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=context['method'], symbol_name=name, entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.event_entries.append(entry)
            added = True

        if not added:
            entry = IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=context['method'], symbol_name=name, entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=''
            )
            result.field_entries.append(entry)


def find_steam_scripts(steam_scripts_dir: Path) -> List[Dict]:
    """Find scripts in SteamScripts directory (folders with Script.cs file)"""
    scripts = []
    if not steam_scripts_dir.exists():
        return scripts

    for item in steam_scripts_dir.iterdir():
        if item.is_dir():
            script_file = item / "Script.cs"
            if script_file.exists():
                scripts.append({
                    "id": item.name,
                    "name": item.name,
                    "source": "steam",
                    "path": str(item.relative_to(SCRIPT_DIR))
                })
    return scripts


def find_local_scripts(local_scripts_dir: Path) -> List[Dict]:
    """Find scripts in LocalScripts directory"""
    scripts = []
    if not local_scripts_dir.exists():
        return scripts

    for item in local_scripts_dir.iterdir():
        if item.is_dir():
            if any(item.rglob("*.cs")):
                scripts.append({
                    "id": item.name,
                    "name": item.name,
                    "source": "local",
                    "path": str(item.relative_to(SCRIPT_DIR))
                })
    return scripts


class ScriptCodeIndexer:
    """Indexes script C# source code using Tree-sitter with parallel processing"""

    def __init__(self):
        self.root_path = SCRIPT_DIR

        self.namespace_index: List[IndexEntry] = []
        self.interface_index: List[IndexEntry] = []
        self.class_index: List[IndexEntry] = []
        self.struct_index: List[IndexEntry] = []
        self.enum_index: List[IndexEntry] = []
        self.method_index: List[IndexEntry] = []
        self.field_index: List[IndexEntry] = []
        self.property_index: List[IndexEntry] = []
        self.event_index: List[IndexEntry] = []
        self.constructor_index: List[IndexEntry] = []
        self.signature_index: List[SignatureEntry] = []

        self.class_hierarchy_index: List[ClassHierarchyEntry] = []
        self.interface_hierarchy_index: List[InterfaceHierarchyEntry] = []
        self.interface_implementation_index: List[InterfaceImplementationEntry] = []

        self.declared_namespaces: Set[str] = set()
        self.declared_interfaces: Dict[str, Set[tuple]] = {}
        self.declared_classes: Dict[str, Set[tuple]] = {}
        self.declared_structs: Dict[str, Set[tuple]] = {}
        self.declared_enums: Dict[str, Set[tuple]] = {}
        self.declared_methods: Dict[str, Set[tuple]] = {}
        self.declared_properties: Dict[str, Set[tuple]] = {}
        self.declared_events: Dict[str, Set[tuple]] = {}
        self.declared_constructors: Dict[str, Set[tuple]] = {}

        self.num_workers = cpu_count() * 2

    @staticmethod
    def _create_batches(files: List[Path], batch_size: int) -> List[List[Path]]:
        batches = []
        for i in range(0, len(files), batch_size):
            batches.append(files[i:i + batch_size])
        return batches

    def _merge_batch_results(self, batch_results: List[List[FileProcessingResult]]):
        for batch in batch_results:
            for result in batch:
                self.namespace_index.extend(result.namespace_entries)
                self.interface_index.extend(result.interface_entries)
                self.class_index.extend(result.class_entries)
                self.struct_index.extend(result.struct_entries)
                self.enum_index.extend(result.enum_entries)
                self.method_index.extend(result.method_entries)
                self.field_index.extend(result.field_entries)
                self.property_index.extend(result.property_entries)
                self.event_index.extend(result.event_entries)
                self.constructor_index.extend(result.constructor_entries)
                self.signature_index.extend(result.signature_entries)
                self.class_hierarchy_index.extend(result.class_hierarchy_entries)
                self.interface_hierarchy_index.extend(result.interface_hierarchy_entries)
                self.interface_implementation_index.extend(result.interface_implementation_entries)

    def _merge_batch_declarations(self, batch_results: List[List[FileProcessingResult]]):
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

                for name, locations in result.declared_properties.items():
                    if name not in self.declared_properties:
                        self.declared_properties[name] = set()
                    self.declared_properties[name].update(locations)

                for name, locations in result.declared_events.items():
                    if name not in self.declared_events:
                        self.declared_events[name] = set()
                    self.declared_events[name].update(locations)

                for name, locations in result.declared_constructors.items():
                    if name not in self.declared_constructors:
                        self.declared_constructors[name] = set()
                    self.declared_constructors[name].update(locations)

    def collect_files(self) -> Tuple[List[Path], List[Dict]]:
        cs_files = []
        all_scripts = []

        steam_scripts = find_steam_scripts(STEAM_SCRIPTS_DIR)
        for script in steam_scripts:
            script_path = SCRIPT_DIR / script["path"]
            cs_files.extend(script_path.rglob("*.cs"))
        all_scripts.extend(steam_scripts)

        local_scripts = find_local_scripts(LOCAL_SCRIPTS_DIR)
        for script in local_scripts:
            script_path = SCRIPT_DIR / script["path"]
            cs_files.extend(script_path.rglob("*.cs"))
        all_scripts.extend(local_scripts)

        return cs_files, all_scripts

    def index_files(self, cs_files: List[Path]):
        total_files = len(cs_files)

        if total_files == 0:
            print("No C# files found to index.")
            return

        print(f"Found {total_files} C# files to index...")
        print(f"Using {self.num_workers} parallel workers")

        random.shuffle(cs_files)

        batch_size = 32
        batches = self._create_batches(cs_files, batch_size)
        print(f"Processing in {len(batches)} batches of up to {batch_size} files each")

        print("\nPass 1: Collecting declarations...")
        root_path_str = str(self.root_path)
        pass1_args = [(batch, root_path_str, False, None) for batch in batches]

        with Pool(processes=self.num_workers) as pool:
            pass1_results = list(pool.imap_unordered(_process_batch_worker, pass1_args))

        self._merge_batch_results(pass1_results)
        self._merge_batch_declarations(pass1_results)
        print(f"Completed pass 1: {total_files} files.")

        shared_declarations = {
            'namespaces': self.declared_namespaces,
            'interfaces': self.declared_interfaces,
            'classes': self.declared_classes,
            'structs': self.declared_structs,
            'enums': self.declared_enums,
            'methods': self.declared_methods,
            'properties': self.declared_properties,
            'events': self.declared_events,
            'constructors': self.declared_constructors,
        }

        print("\nPass 2: Collecting usages...")
        pass2_args = [(batch, root_path_str, True, shared_declarations) for batch in batches]

        with Pool(processes=self.num_workers) as pool:
            pass2_results = list(pool.imap_unordered(_process_batch_worker, pass2_args))

        self._merge_batch_results(pass2_results)
        print(f"Completed pass 2: {total_files} files.")

    def write_indices(self, output_dir: Path, scripts: List[Dict]):
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(SCRIPT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump({"scripts": scripts}, f, indent=2)
        print(f"Written script list to {SCRIPT_LIST_FILE}")

        def split_entries(entries):
            declarations = [e for e in entries if e.entry_type == 'declaration']
            usages = [e for e in entries if e.entry_type == 'usage']
            return declarations, usages

        categories = [
            ('namespace', self.namespace_index),
            ('interface', self.interface_index),
            ('class', self.class_index),
            ('struct', self.struct_index),
            ('enum', self.enum_index),
            ('method', self.method_index),
            ('field', self.field_index),
            ('property', self.property_index),
            ('event', self.event_index),
            ('constructor', self.constructor_index),
        ]

        total_declarations = 0
        total_usages = 0

        for category_name, index_data in categories:
            declarations, usages = split_entries(index_data)
            total_declarations += len(declarations)
            total_usages += len(usages)

            def sort_key(e):
                return (e.namespace, e.declaring_type, e.method, e.symbol_name,
                        e.file_path, e.start_line, e.end_line)

            sorted_declarations = sorted(declarations, key=sort_key)
            sorted_usages = sorted(usages, key=sort_key)

            decl_path = output_dir / f"{category_name}_declarations.csv"
            print(f"Writing {len(sorted_declarations)} declaration entries to {decl_path}...")

            with open(decl_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(IndexEntry.csv_header())
                for entry in sorted_declarations:
                    writer.writerow(entry.to_csv_row())

            usage_path = output_dir / f"{category_name}_usages.csv"
            print(f"Writing {len(sorted_usages)} usage entries to {usage_path}...")

            with open(usage_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(IndexEntry.csv_header())
                for entry in sorted_usages:
                    writer.writerow(entry.to_csv_row())

        def sig_sort_key(e):
            return (e.namespace, e.declaring_type, e.method_name, e.file_path, e.start_line, e.end_line)

        sorted_signatures = sorted(self.signature_index, key=sig_sort_key)
        sig_path = output_dir / "method_signatures.csv"
        print(f"Writing {len(sorted_signatures)} signature entries to {sig_path}...")

        with open(sig_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(SignatureEntry.csv_header())
            for entry in sorted_signatures:
                writer.writerow(entry.to_csv_row())

        sorted_class_hierarchy = sorted(self.class_hierarchy_index,
            key=lambda e: (e.child_namespace, e.child_class, e.parent_namespace, e.parent_class))
        class_hier_path = output_dir / "class_hierarchy.csv"
        print(f"Writing {len(sorted_class_hierarchy)} class hierarchy entries to {class_hier_path}...")

        with open(class_hier_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(ClassHierarchyEntry.csv_header())
            for entry in sorted_class_hierarchy:
                writer.writerow(entry.to_csv_row())

        sorted_interface_hierarchy = sorted(self.interface_hierarchy_index,
            key=lambda e: (e.child_namespace, e.child_interface, e.parent_namespace, e.parent_interface))
        interface_hier_path = output_dir / "interface_hierarchy.csv"
        print(f"Writing {len(sorted_interface_hierarchy)} interface hierarchy entries to {interface_hier_path}...")

        with open(interface_hier_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(InterfaceHierarchyEntry.csv_header())
            for entry in sorted_interface_hierarchy:
                writer.writerow(entry.to_csv_row())

        sorted_implementations = sorted(self.interface_implementation_index,
            key=lambda e: (e.implementing_namespace, e.implementing_type, e.interfaces))
        impl_path = output_dir / "interface_implementation.csv"
        print(f"Writing {len(sorted_implementations)} interface implementation entries to {impl_path}...")

        with open(impl_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(InterfaceImplementationEntry.csv_header())
            for entry in sorted_implementations:
                writer.writerow(entry.to_csv_row())

        print("\nGenerating hierarchy tree visualizations...")

        from hierarchy_tree import build_class_tree, build_interface_tree

        if sorted_class_hierarchy:
            class_tree_data = [(e.child_namespace, e.child_class, e.parent_namespace, e.parent_class)
                              for e in sorted_class_hierarchy]
            class_tree_text = build_class_tree(class_tree_data)
            class_tree_path = output_dir / "class_hierarchy.txt"
            with open(class_tree_path, 'w', encoding='utf-8') as f:
                f.write(class_tree_text)
            print(f"Written class hierarchy tree to {class_tree_path}")

        if sorted_interface_hierarchy:
            interface_tree_data = [(e.child_namespace, e.child_interface, e.parent_namespace, e.parent_interface)
                                   for e in sorted_interface_hierarchy]
            interface_tree_text = build_interface_tree(interface_tree_data)
            interface_tree_path = output_dir / "interface_hierarchy.txt"
            with open(interface_tree_path, 'w', encoding='utf-8') as f:
                f.write(interface_tree_text)
            print(f"Written interface hierarchy tree to {interface_tree_path}")

        print(f"\nAll index files written to {output_dir}")
        print(f"  - Total declarations: {total_declarations} entries")
        print(f"  - Total usages: {total_usages} entries")
        print(f"  - Total signatures: {len(sorted_signatures)} entries")
        print(f"  - Class hierarchy: {len(sorted_class_hierarchy)} entries")
        print(f"  - Interface hierarchy: {len(sorted_interface_hierarchy)} entries")
        print(f"  - Interface implementations: {len(sorted_implementations)} entries")


def main():
    sys.setrecursionlimit(10000)

    print("PB Script Code Indexer")
    print("=" * 50)
    print(f"Steam scripts directory: {STEAM_SCRIPTS_DIR}")
    print(f"Local scripts directory: {LOCAL_SCRIPTS_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    indexer = ScriptCodeIndexer()
    cs_files, scripts = indexer.collect_files()

    print(f"Found {len(scripts)} scripts:")
    for script in scripts:
        print(f"  - [{script['source']}] {script['name']}")
    print()

    indexer.index_files(cs_files)
    indexer.write_indices(OUTPUT_DIR, scripts)

    print("\nIndexing complete!")


if __name__ == '__main__':
    main()
