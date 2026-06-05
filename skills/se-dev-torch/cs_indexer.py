#!/usr/bin/env python3
"""
Tree-sitter based C# parser used by index_torch.py.

This module is the per-file parser only. Orchestration (which files to parse
and how CSV output is written) lives in index_torch.py.
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from tree_sitter import Language, Node, Parser
from tree_sitter_c_sharp import language


@dataclass
class IndexEntry:
    namespace: str
    declaring_type: str
    method: str
    symbol_name: str
    entry_type: str
    file_path: str
    start_line: int
    end_line: int
    description: str
    access: str = ""
    modifiers: str = ""
    member_type: str = ""
    params: str = ""

    def to_csv_row(self) -> List[str]:
        return [
            self.namespace, self.declaring_type, self.method, self.symbol_name,
            self.entry_type, self.file_path, str(self.start_line), str(self.end_line),
            self.description, self.access, self.modifiers, self.member_type, self.params,
        ]

    @staticmethod
    def csv_header() -> List[str]:
        return [
            'namespace', 'declaring_type', 'method', 'symbol_name', 'type',
            'file_path', 'start_line', 'end_line', 'description',
            'access', 'modifiers', 'member_type', 'params',
        ]


@dataclass
class SignatureEntry:
    namespace: str
    declaring_type: str
    method_name: str
    signature: str
    file_path: str
    start_line: int
    end_line: int
    description: str

    def to_csv_row(self) -> List[str]:
        return [
            self.namespace, self.declaring_type, self.method_name, self.signature,
            self.file_path, str(self.start_line), str(self.end_line), self.description,
        ]

    @staticmethod
    def csv_header() -> List[str]:
        return [
            'namespace', 'declaring_type', 'method_name', 'signature',
            'file_path', 'start_line', 'end_line', 'description',
        ]


@dataclass
class ClassHierarchyEntry:
    child_namespace: str
    child_class: str
    parent_namespace: str
    parent_class: str
    file_path: str
    start_line: int
    end_line: int

    def to_csv_row(self) -> List[str]:
        return [
            self.child_namespace, self.child_class, self.parent_namespace,
            self.parent_class, self.file_path, str(self.start_line), str(self.end_line),
        ]

    @staticmethod
    def csv_header() -> List[str]:
        return [
            'child_namespace', 'child_class', 'parent_namespace', 'parent_class',
            'file_path', 'start_line', 'end_line',
        ]


@dataclass
class InterfaceHierarchyEntry:
    child_namespace: str
    child_interface: str
    parent_namespace: str
    parent_interface: str
    file_path: str
    start_line: int
    end_line: int

    def to_csv_row(self) -> List[str]:
        return [
            self.child_namespace, self.child_interface, self.parent_namespace,
            self.parent_interface, self.file_path, str(self.start_line), str(self.end_line),
        ]

    @staticmethod
    def csv_header() -> List[str]:
        return [
            'child_namespace', 'child_interface', 'parent_namespace', 'parent_interface',
            'file_path', 'start_line', 'end_line',
        ]


@dataclass
class InterfaceImplementationEntry:
    implementing_namespace: str
    implementing_type: str
    interfaces: str
    file_path: str
    start_line: int
    end_line: int

    def to_csv_row(self) -> List[str]:
        return [
            self.implementing_namespace, self.implementing_type, self.interfaces,
            self.file_path, str(self.start_line), str(self.end_line),
        ]

    @staticmethod
    def csv_header() -> List[str]:
        return [
            'implementing_namespace', 'implementing_type', 'interfaces',
            'file_path', 'start_line', 'end_line',
        ]


@dataclass
class FileProcessingResult:
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

    class_hierarchy_entries: List[ClassHierarchyEntry] = field(default_factory=list)
    interface_hierarchy_entries: List[InterfaceHierarchyEntry] = field(default_factory=list)
    interface_implementation_entries: List[InterfaceImplementationEntry] = field(default_factory=list)

    declared_namespaces: Set[str] = field(default_factory=set)
    declared_interfaces: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_classes: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_structs: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_enums: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_methods: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_properties: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_events: Dict[str, Set[tuple]] = field(default_factory=dict)
    declared_constructors: Dict[str, Set[tuple]] = field(default_factory=dict)


class FileProcessor:
    """Processes a single C# file using Tree-sitter."""

    _ACCESS_KEYWORDS = frozenset({"public", "private", "protected", "internal"})
    _MODIFIER_KEYWORDS = frozenset({
        "static", "readonly", "const", "volatile", "virtual", "override",
        "abstract", "sealed", "async", "extern", "new", "unsafe", "partial",
    })

    def __init__(self, root_path: str):
        # Avoid .resolve() so we don't follow the Data junction; otherwise
        # file_path.relative_to(self.root_path) fails when files come in via
        # the junction path.
        self.root_path = Path(root_path)
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

    def process_file(self, file_path: Path, collect_usages: bool,
                     path_label: Optional[str] = None) -> FileProcessingResult:
        result = FileProcessingResult()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                source_code = f.read()

        tree = self.parser.parse(bytes(source_code, 'utf-8'))
        if path_label is not None:
            relative_path = path_label
        else:
            relative_path = str(file_path.relative_to(self.root_path))

        source_lines = source_code.split('\n')

        context = {
            'namespace': '', 'declaring_type': '', 'method': '',
            'file_path': relative_path, 'source_lines': source_lines,
            'collect_usages': collect_usages, 'result': result,
        }

        self._traverse_tree(tree.root_node, context)
        return result

    def _traverse_tree(self, node: Node, context: Dict):
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

    @staticmethod
    def _build_namespace(current: str, new: str) -> str:
        return f"{current}.{new}" if current else new

    @staticmethod
    def _get_preceding_comment(node: Node, source_lines: List[str]) -> str:
        start_line = node.start_point[0]
        if start_line == 0:
            return ''
        comment_lines: List[str] = []
        current_line = start_line - 1
        while current_line >= 0:
            line = source_lines[current_line].strip()
            if line.startswith('//'):
                comment_lines.insert(0, line[2:].strip())
                current_line -= 1
            elif line.endswith('*/'):
                multi_line_parts: List[str] = []
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

    def _extract_modifiers(self, node: Node) -> tuple:
        access_parts, modifier_parts = [], []
        for child in node.children:
            if child.type == "modifier":
                for kw in child.children:
                    if kw.type in self._ACCESS_KEYWORDS:
                        access_parts.append(kw.type)
                    elif kw.type in self._MODIFIER_KEYWORDS:
                        modifier_parts.append(kw.type)
        return (" ".join(access_parts), " ".join(modifier_parts))

    @staticmethod
    def _extract_full_type_text(type_node: Optional[Node]) -> str:
        if type_node is None:
            return ""
        text = type_node.text
        return text.decode("utf-8") if text else ""

    @staticmethod
    def _extract_params_text(node: Node) -> str:
        for child in node.children:
            if child.type == "parameter_list":
                text = child.text
                if text:
                    return re.sub(r"\s+", " ", text.decode("utf-8")).strip()
        return ""

    @staticmethod
    def _extract_type_name(node: Node) -> Optional[str]:
        if node.type in ('identifier', 'qualified_name'):
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
                t = self._extract_type_name(child)
                if t:
                    types.append(t)
        return types

    @staticmethod
    def _find_base_list(node: Node) -> Optional[Node]:
        for child in node.children:
            if child.type == 'base_list':
                return child
        return None

    def _resolve_type_namespace(self, type_name: str, current_namespace: str) -> str:
        if '.' in type_name:
            return type_name
        full_name = f"{current_namespace}.{type_name}" if current_namespace else type_name
        for declared in (self.declared_interfaces, self.declared_classes, self.declared_structs):
            if type_name in declared:
                locations = declared[type_name]
                for ns, _ in locations:
                    if ns == current_namespace:
                        return full_name
                if locations:
                    ns, _ = next(iter(locations))
                    return f"{ns}.{type_name}" if ns else type_name
        return full_name

    @staticmethod
    def _split_namespace_and_type(fully_qualified: str) -> Tuple[str, str]:
        if '.' not in fully_qualified:
            return ('', fully_qualified)
        ns, name = fully_qualified.rsplit('.', 1)
        return (ns, name)

    def _extract_method_signature(self, node: Node, source_lines: List[str]) -> Tuple[str, int, int]:
        start_line, start_col = node.start_point
        body_node = None
        semicolon_pos = None
        for child in node.children:
            if child.type in ('block', 'arrow_expression_clause'):
                body_node = child
                break
            if child.type == ';':
                semicolon_pos = (child.start_point[0], child.start_point[1])
        if body_node:
            end_line, end_col = body_node.start_point
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
        normalized = re.sub(r'\s+', ' ', ' '.join(sig_parts)).strip()
        sig_end_line = end_line if end_line > start_line else end_line + 1
        return (normalized, start_line + 1, sig_end_line)

    def _process_file_scoped_namespace(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        context['namespace'] = name
        result.declared_namespaces.add(name)
        result.namespace_entries.append(IndexEntry(
            namespace=name, declaring_type='', method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=self._get_preceding_comment(node, context['source_lines']),
        ))

    def _process_namespace(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        full_namespace = self._build_namespace(context['namespace'], name)
        context['namespace'] = full_namespace
        result.declared_namespaces.add(full_namespace)
        result.namespace_entries.append(IndexEntry(
            namespace=full_namespace, declaring_type='', method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=self._get_preceding_comment(node, context['source_lines']),
        ))

    def _process_interface(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        context['declaring_type'] = name
        result.declared_interfaces.setdefault(name, set()).add((context['namespace'], ''))
        result.interface_entries.append(IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=self._get_preceding_comment(node, context['source_lines']),
        ))

    def _process_type_hierarchy(self, node, context, result):
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
            for parent_type in base_types:
                parent_fqn = self._resolve_type_namespace(parent_type, context['namespace'])
                parent_ns, parent_name = self._split_namespace_and_type(parent_fqn)
                result.interface_hierarchy_entries.append(InterfaceHierarchyEntry(
                    child_namespace=context['namespace'], child_interface=name,
                    parent_namespace=parent_ns, parent_interface=parent_name,
                    file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                ))
        elif node.type == 'struct_declaration':
            interface_fqns = [self._resolve_type_namespace(i, context['namespace'])
                              for i in base_types]
            result.interface_implementation_entries.append(InterfaceImplementationEntry(
                implementing_namespace=context['namespace'], implementing_type=name,
                interfaces=','.join(interface_fqns), file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            ))
        else:
            first_type = base_types[0]
            first_fqn = self._resolve_type_namespace(first_type, context['namespace'])
            first_ns, first_name = self._split_namespace_and_type(first_fqn)
            is_interface = first_name in self.declared_interfaces

            if is_interface:
                interfaces = base_types
            else:
                result.class_hierarchy_entries.append(ClassHierarchyEntry(
                    child_namespace=context['namespace'], child_class=name,
                    parent_namespace=first_ns, parent_class=first_name,
                    file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                ))
                interfaces = base_types[1:]

            if interfaces:
                interface_fqns = [self._resolve_type_namespace(i, context['namespace'])
                                  for i in interfaces]
                result.interface_implementation_entries.append(InterfaceImplementationEntry(
                    implementing_namespace=context['namespace'], implementing_type=name,
                    interfaces=','.join(interface_fqns), file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                ))

    def _process_class(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        context['declaring_type'] = name
        result.declared_classes.setdefault(name, set()).add((context['namespace'], ''))
        result.class_entries.append(IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=self._get_preceding_comment(node, context['source_lines']),
        ))

    def _process_struct(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        context['declaring_type'] = name
        result.declared_structs.setdefault(name, set()).add((context['namespace'], ''))
        result.struct_entries.append(IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=self._get_preceding_comment(node, context['source_lines']),
        ))

    def _process_enum(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        context['declaring_type'] = name
        result.declared_enums.setdefault(name, set()).add((context['namespace'], ''))
        result.enum_entries.append(IndexEntry(
            namespace=context['namespace'], declaring_type=name, method='', symbol_name='',
            entry_type='declaration', file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=self._get_preceding_comment(node, context['source_lines']),
        ))

    def _process_method(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        is_constructor = node.type == 'constructor_declaration'
        context['method'] = name
        result.declared_methods.setdefault(name, set()).add(
            (context['namespace'], context['declaring_type']))
        if is_constructor:
            result.declared_constructors.setdefault(name, set()).add(
                (context['namespace'], context['declaring_type']))

        access, modifiers = self._extract_modifiers(node)
        params_text = self._extract_params_text(node)

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
            description=description, access=access, modifiers=modifiers,
            member_type=return_type, params=params_text,
        )
        if is_constructor:
            result.constructor_entries.append(entry)
        else:
            result.method_entries.append(entry)

        sig_text, sig_start, sig_end = self._extract_method_signature(node, context['source_lines'])
        result.signature_entries.append(SignatureEntry(
            namespace=context['namespace'], declaring_type=context['declaring_type'],
            method_name=name, signature=sig_text, file_path=context['file_path'],
            start_line=sig_start, end_line=sig_end, description=description,
        ))

    def _process_field(self, node, context, result):
        access, modifiers = self._extract_modifiers(node)
        for child in node.children:
            if child.type == 'variable_declaration':
                type_text = ""
                for vc in child.children:
                    if vc.type not in ("variable_declarator", ",", ";"):
                        type_text = self._extract_full_type_text(vc)
                        break
                for declarator in child.children:
                    if declarator.type == 'variable_declarator':
                        name = self._get_identifier_name(declarator)
                        if name:
                            result.field_entries.append(IndexEntry(
                                namespace=context['namespace'],
                                declaring_type=context['declaring_type'],
                                method='', symbol_name=name, entry_type='declaration',
                                file_path=context['file_path'],
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                description=self._get_preceding_comment(
                                    node, context['source_lines']),
                                access=access, modifiers=modifiers, member_type=type_text,
                            ))

    def _process_property(self, node, context, result):
        name = self._get_identifier_name(node)
        if not name:
            return
        result.declared_properties.setdefault(name, set()).add(
            (context['namespace'], context['declaring_type']))
        access, modifiers = self._extract_modifiers(node)
        type_text = ""
        for child in node.children:
            if child.type not in ("modifier", "identifier", "accessor_list",
                                  "arrow_expression_clause", "=", ";", "{", "}"):
                type_text = self._extract_full_type_text(child)
                break
        result.property_entries.append(IndexEntry(
            namespace=context['namespace'], declaring_type=context['declaring_type'],
            method='', symbol_name=name, entry_type='declaration',
            file_path=context['file_path'],
            start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
            description=self._get_preceding_comment(node, context['source_lines']),
            access=access, modifiers=modifiers, member_type=type_text,
        ))

    def _process_event(self, node, context, result):
        access, modifiers = self._extract_modifiers(node)
        if node.type == "event_field_declaration":
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
                                result.declared_events.setdefault(name, set()).add(
                                    (context['namespace'], context['declaring_type']))
                                result.event_entries.append(IndexEntry(
                                    namespace=context['namespace'],
                                    declaring_type=context['declaring_type'],
                                    method='', symbol_name=name, entry_type='declaration',
                                    file_path=context['file_path'],
                                    start_line=node.start_point[0] + 1,
                                    end_line=node.end_point[0] + 1,
                                    description=self._get_preceding_comment(
                                        node, context['source_lines']),
                                    access=access, modifiers=modifiers, member_type=type_text,
                                ))
        else:
            name = self._get_identifier_name(node)
            if not name:
                return
            result.declared_events.setdefault(name, set()).add(
                (context['namespace'], context['declaring_type']))
            type_text = ""
            found_event_keyword = False
            for child in node.children:
                if child.type == "event":
                    found_event_keyword = True
                elif (found_event_keyword and child.type != "identifier"
                      and child.type != "accessor_list" and child.type != ";"):
                    type_text = self._extract_full_type_text(child)
                    break
            result.event_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method='', symbol_name=name, entry_type='declaration',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description=self._get_preceding_comment(node, context['source_lines']),
                access=access, modifiers=modifiers, member_type=type_text,
            ))

    def _process_identifier_usage(self, node, context, result):
        parent = node.parent
        if not parent:
            return
        declaration_types = {
            'namespace_declaration', 'interface_declaration', 'class_declaration',
            'struct_declaration', 'record_declaration', 'enum_declaration',
            'method_declaration', 'constructor_declaration', 'field_declaration',
            'property_declaration', 'variable_declaration', 'variable_declarator',
            'parameter', 'type_parameter', 'using_directive', 'qualified_name',
            'member_access_expression',
        }
        if parent.type in declaration_types:
            return
        grandparent = parent.parent
        if grandparent and grandparent.type in declaration_types:
            return

        name = node.text.decode('utf-8')
        added = False

        if name in self.declared_namespaces:
            result.namespace_entries.append(IndexEntry(
                namespace=name, declaring_type='', method='', symbol_name='',
                entry_type='usage', file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True
        if name in self.declared_interfaces:
            result.interface_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True
        if name in self.declared_classes:
            result.class_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True
        if name in self.declared_structs:
            result.struct_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True
        if name in self.declared_enums:
            result.enum_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=name,
                method=context['method'], symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True
        if name in self.declared_methods:
            result.method_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=name, symbol_name='', entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True
        if name in self.declared_constructors:
            is_ctor = False
            p = parent
            while p:
                if p.type == "object_creation_expression":
                    is_ctor = True
                    break
                if p.type in ("argument_list", "qualified_name"):
                    p = p.parent
                else:
                    break
            if is_ctor:
                result.constructor_entries.append(IndexEntry(
                    namespace=context['namespace'], declaring_type=context['declaring_type'],
                    method=name, symbol_name='', entry_type='usage',
                    file_path=context['file_path'],
                    start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                    description='',
                ))
                added = True
        if name in self.declared_properties:
            result.property_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=context['method'], symbol_name=name, entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True
        if name in self.declared_events:
            result.event_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=context['method'], symbol_name=name, entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))
            added = True

        if not added:
            result.field_entries.append(IndexEntry(
                namespace=context['namespace'], declaring_type=context['declaring_type'],
                method=context['method'], symbol_name=name, entry_type='usage',
                file_path=context['file_path'],
                start_line=node.start_point[0] + 1, end_line=node.end_point[0] + 1,
                description='',
            ))


# CSV header registry, indexed by the basename of an output file.
INDEX_ENTRY_FILES = {
    'namespace_declarations.csv', 'namespace_usages.csv',
    'interface_declarations.csv', 'interface_usages.csv',
    'class_declarations.csv', 'class_usages.csv',
    'struct_declarations.csv', 'struct_usages.csv',
    'enum_declarations.csv', 'enum_usages.csv',
    'method_declarations.csv', 'method_usages.csv',
    'field_declarations.csv', 'field_usages.csv',
    'property_declarations.csv', 'property_usages.csv',
    'event_declarations.csv', 'event_usages.csv',
    'constructor_declarations.csv', 'constructor_usages.csv',
}
SIGNATURE_FILE = 'method_signatures.csv'
CLASS_HIERARCHY_FILE = 'class_hierarchy.csv'
INTERFACE_HIERARCHY_FILE = 'interface_hierarchy.csv'
INTERFACE_IMPL_FILE = 'interface_implementation.csv'
