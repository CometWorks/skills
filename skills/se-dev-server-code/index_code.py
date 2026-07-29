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
import re
import sys
from dataclasses import dataclass, field
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from tree_sitter import Language, Parser, Node
from tree_sitter_c_sharp import language


# `interface_implementation.csv` packs every implemented interface into one
# field. Generic arguments are preserved, so that field can contain commas
# (`ICallSite<IMyEventOwner, string, DBNull>`) and a comma cannot also be the
# list separator. Semicolon never appears in a C# type name.
INTERFACE_SEPARATOR = ";"


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
    access: str = (
        ""  # Access modifier: public, private, protected, internal, protected internal
    )
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
            "namespace",
            "declaring_type",
            "method",
            "symbol_name",
            "type",
            "file_path",
            "start_line",
            "end_line",
            "description",
            "access",
            "modifiers",
            "member_type",
            "params",
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
            self.description,
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            "namespace",
            "declaring_type",
            "method_name",
            "signature",
            "file_path",
            "start_line",
            "end_line",
            "description",
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
            str(self.end_line),
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            "child_namespace",
            "child_class",
            "parent_namespace",
            "parent_class",
            "file_path",
            "start_line",
            "end_line",
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
            str(self.end_line),
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            "child_namespace",
            "child_interface",
            "parent_namespace",
            "parent_interface",
            "file_path",
            "start_line",
            "end_line",
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
            str(self.end_line),
        ]

    @staticmethod
    def csv_header() -> List[str]:
        """Return CSV header row"""
        return [
            "implementing_namespace",
            "implementing_type",
            "interfaces",
            "file_path",
            "start_line",
            "end_line",
        ]


@dataclass
class FileProcessingResult:
    """Results from processing a single file"""

    namespace_entries: List[IndexEntry] = field(default_factory=list)
    interface_entries: List[IndexEntry] = field(default_factory=list)
    class_entries: List[IndexEntry] = field(default_factory=list)
    struct_entries: List[IndexEntry] = field(default_factory=list)
    enum_entries: List[IndexEntry] = field(default_factory=list)
    enum_member_entries: List[IndexEntry] = field(default_factory=list)
    method_entries: List[IndexEntry] = field(default_factory=list)
    field_entries: List[IndexEntry] = field(default_factory=list)
    property_entries: List[IndexEntry] = field(default_factory=list)
    event_entries: List[IndexEntry] = field(default_factory=list)
    constructor_entries: List[IndexEntry] = field(default_factory=list)
    signature_entries: List[SignatureEntry] = field(default_factory=list)

    # Hierarchy entries
    class_hierarchy_entries: List[ClassHierarchyEntry] = field(default_factory=list)
    interface_hierarchy_entries: List[InterfaceHierarchyEntry] = field(
        default_factory=list
    )
    interface_implementation_entries: List[InterfaceImplementationEntry] = field(
        default_factory=list
    )

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

    # Increase recursion limit for deeply nested code (default is 1000)
    sys.setrecursionlimit(10000)

    processor = FileProcessor(root_path)

    if collect_usages and shared_declarations:
        # Pass 2: use shared declarations
        processor.declared_namespaces = shared_declarations["namespaces"]
        processor.declared_interfaces = shared_declarations["interfaces"]
        processor.declared_classes = shared_declarations["classes"]
        processor.declared_structs = shared_declarations["structs"]
        processor.declared_enums = shared_declarations["enums"]
        processor.declared_methods = shared_declarations["methods"]
        processor.declared_properties = shared_declarations["properties"]
        processor.declared_events = shared_declarations["events"]
        processor.declared_constructors = shared_declarations["constructors"]

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
        self.declared_properties: Dict[str, Set[tuple]] = {}
        self.declared_events: Dict[str, Set[tuple]] = {}
        self.declared_constructors: Dict[str, Set[tuple]] = {}

    def process_file(
        self, file_path: Path, collect_usages: bool
    ) -> FileProcessingResult:
        """Process a single C# file and return results"""
        result = FileProcessingResult()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                source_code = f.read()

        tree = self.parser.parse(bytes(source_code, "utf-8"))
        relative_path = str(file_path.relative_to(self.root_path))

        source_lines = source_code.split("\n")

        context = {
            "namespace": "",
            "declaring_type": "",
            "method": "",
            "file_path": relative_path,
            "source_lines": source_lines,
            "collect_usages": collect_usages,
            "result": result,
        }

        self._traverse_tree(tree.root_node, context)

        # A handful of decompiled files contain constructs the C# grammar
        # rejects (unsafe pointer dereferences such as
        # `return ref *(HkTransform*)ptr.ToPointer();`, and
        # `private virtual sealed object CreateInstance()`). Tree-sitter
        # degrades the enclosing type into an ERROR node, so its declaration
        # is never dispatched and the type becomes invisible to every
        # consumer. Recover those declarations from the source text.
        if tree.root_node.has_error:
            self._recover_from_parse_errors(context, result, collect_usages)

        return result

    def _traverse_tree(self, node: Node, context: Dict):
        """Recursively traverse the syntax tree"""
        prev_namespace = context["namespace"]
        prev_declaring_type = context["declaring_type"]
        prev_method = context["method"]
        is_file_scoped_namespace = False
        result = context["result"]

        if context["collect_usages"]:
            if node.type == "file_scoped_namespace_declaration":
                name = self._get_identifier_name(node)
                if name:
                    context["namespace"] = name
                    is_file_scoped_namespace = True
            elif node.type == "namespace_declaration":
                name = self._get_identifier_name(node)
                if name:
                    context["namespace"] = self._build_namespace(
                        context["namespace"], name
                    )
            elif node.type in (
                "interface_declaration",
                "class_declaration",
                "struct_declaration",
                "record_declaration",
                "enum_declaration",
            ):
                name = self._get_identifier_name(node)
                if name:
                    context["declaring_type"] = name
                # Process hierarchy/implementation in Pass 2 where
                # declared_interfaces is populated from all files
                if node.type != "enum_declaration":
                    self._process_type_hierarchy(node, context, result)
            elif node.type in ("method_declaration", "constructor_declaration"):
                name = self._get_identifier_name(node)
                if name:
                    context["method"] = name
            elif node.type == "identifier":
                self._process_identifier_usage(node, context, result)
        else:
            if node.type == "file_scoped_namespace_declaration":
                self._process_file_scoped_namespace(node, context, result)
                is_file_scoped_namespace = True
            elif node.type == "namespace_declaration":
                self._process_namespace(node, context, result)
            elif node.type == "interface_declaration":
                self._process_interface(node, context, result)
            elif node.type == "class_declaration":
                self._process_class(node, context, result)
            elif node.type == "struct_declaration":
                self._process_struct(node, context, result)
            elif node.type == "enum_declaration":
                self._process_enum(node, context, result)
            elif node.type == "record_declaration":
                self._process_class(node, context, result)
            elif node.type in ("method_declaration", "constructor_declaration"):
                self._process_method(node, context, result)
            elif node.type == "field_declaration":
                self._process_field(node, context, result)
            elif node.type == "property_declaration":
                self._process_property(node, context, result)
            elif node.type in ("event_field_declaration", "event_declaration"):
                self._process_event(node, context, result)

        for child in node.children:
            self._traverse_tree(child, context)

        if not is_file_scoped_namespace:
            context["namespace"] = prev_namespace
        context["declaring_type"] = prev_declaring_type
        context["method"] = prev_method

    # Matches a type declaration at the start of a line, after optional
    # indentation, attributes and modifiers. Same shape as the ad-hoc detector
    # that originally found the eleven missing types.
    _SCAN_DECL_RE = re.compile(
        r"^\s*(?:\[[^\]]*\]\s*)*"
        r"(?:(?:public|private|protected|internal|static|sealed|abstract|"
        r"partial|unsafe|new|readonly|ref|file|extern)\s+)*"
        r"(?P<kind>class|struct|interface|enum|record)\s+"
        r"(?P<name>[A-Za-z_]\w*)"
    )
    _SCAN_NS_RE = re.compile(r"^\s*namespace\s+(?P<name>[\w.]+)\s*(?P<term>[;{]?)")

    _KIND_TO_ENTRIES = {
        "class": "class_entries",
        "record": "class_entries",
        "struct": "struct_entries",
        "interface": "interface_entries",
        "enum": "enum_entries",
    }
    _KIND_TO_DECLARED = {
        "class": "declared_classes",
        "record": "declared_classes",
        "struct": "declared_structs",
        "interface": "declared_interfaces",
        "enum": "declared_enums",
    }

    @staticmethod
    def _strip_code_noise(line: str, in_block_comment: bool) -> Tuple[str, bool]:
        """Blank out comments, strings and char literals in one line.

        Brace counting has to run on real code only: a `"}"` inside a string
        literal would otherwise close a type early and truncate its span.
        Returns the cleaned line and whether a block comment is still open.
        """
        out = []
        i = 0
        length = len(line)
        while i < length:
            char = line[i]
            if in_block_comment:
                if line.startswith("*/", i):
                    in_block_comment = False
                    i += 2
                else:
                    i += 1
                continue
            if line.startswith("//", i):
                break
            if line.startswith("/*", i):
                in_block_comment = True
                i += 2
                continue
            if line.startswith('@"', i):
                i += 2
                while i < length:
                    if line[i] == '"':
                        if line.startswith('""', i):
                            i += 2
                            continue
                        i += 1
                        break
                    i += 1
                continue
            if char in ('"', "'"):
                quote = char
                i += 1
                while i < length:
                    if line[i] == "\\":
                        i += 2
                        continue
                    if line[i] == quote:
                        i += 1
                        break
                    i += 1
                continue
            out.append(char)
            i += 1
        return "".join(out), in_block_comment

    def _scan_declarations(self, source_lines: List[str]) -> List[Dict]:
        """Find every type declaration in a file by reading its text.

        Returns dicts of kind / name / namespace / start_line / end_line /
        bases, with 1-indexed lines. Spans come from brace matching, so a
        nested type gets its own extent instead of inheriting its parent's.
        """
        declarations: List[Dict] = []
        open_stack: List[Dict] = []
        namespace = ""
        namespace_stack: List[Tuple[int, str]] = []
        pending: Optional[Dict] = None
        depth = 0
        in_block_comment = False

        for index, raw in enumerate(source_lines):
            code, in_block_comment = self._strip_code_noise(raw, in_block_comment)
            if not code.strip():
                continue

            namespace_match = self._SCAN_NS_RE.match(code)
            if namespace_match:
                if namespace_match.group("term") == ";":
                    # File-scoped namespace: applies to the rest of the file.
                    namespace = namespace_match.group("name")
                else:
                    namespace_stack.append((depth, namespace))
                    namespace = namespace_match.group("name")
            else:
                decl_match = self._SCAN_DECL_RE.match(code)
                if decl_match:
                    rest = code[decl_match.end() :]
                    head = rest.split("{", 1)[0].split(" where ", 1)[0]
                    bases: List[str] = []
                    if ":" in head:
                        bases = self._split_base_text(head.split(":", 1)[1])
                    pending = {
                        "kind": decl_match.group("kind"),
                        "name": decl_match.group("name"),
                        "namespace": namespace,
                        "start_line": index + 1,
                        "end_line": index + 1,
                        "bases": bases,
                    }

            for char in code:
                if char == "{":
                    depth += 1
                    if pending is not None:
                        pending["depth"] = depth
                        open_stack.append(pending)
                        declarations.append(pending)
                        pending = None
                elif char == "}":
                    if open_stack and open_stack[-1].get("depth") == depth:
                        open_stack.pop()["end_line"] = index + 1
                    if namespace_stack and namespace_stack[-1][0] == depth - 1:
                        _, namespace = namespace_stack.pop()
                    depth -= 1

        # An unterminated declaration runs to the end of the file.
        for declaration in open_stack:
            declaration["end_line"] = len(source_lines)
        for declaration in declarations:
            declaration.pop("depth", None)
        return declarations

    @staticmethod
    def _split_base_text(text: str) -> List[str]:
        """Split a base list on top-level commas, keeping generic arguments."""
        bases: List[str] = []
        depth = 0
        current: List[str] = []
        for char in text:
            if char in "<([":
                depth += 1
            elif char in ">)]":
                depth -= 1
            if char == "," and depth == 0:
                bases.append("".join(current).strip())
                current = []
                continue
            current.append(char)
        tail = "".join(current).strip()
        if tail:
            bases.append(tail)
        return [b for b in bases if b]

    def _recover_from_parse_errors(
        self, context: Dict, result: FileProcessingResult, collect_usages: bool
    ):
        """Repair a file whose syntax tree came back with ERROR nodes.

        Three separate repairs, all keyed on the source-scanned declarations:

        1. Emit declarations the tree dissolved. Without this the type appears
           in no `*_declarations.csv` at all and is invisible downstream.
        2. Correct spans. An ERROR node hands its own extent to whatever
           declaration tree-sitter recovered inside it, so a 40-line nested
           struct was recorded as spanning its 720-line parent.
        3. Re-attribute members. Every member lexically inside that inflated
           node was recorded against the wrong declaring type.
        """
        scanned = self._scan_declarations(context["source_lines"])
        if not scanned:
            return

        file_path = context["file_path"]

        if collect_usages:
            self._recover_hierarchy(scanned, file_path, result)
            return

        # --- 1 and 2: declarations -----------------------------------------
        by_start: Dict[Tuple[str, int], Dict] = {
            (d["name"], d["start_line"]): d for d in scanned
        }
        seen: Set[Tuple[str, int]] = set()

        for attribute in (
            "class_entries",
            "struct_entries",
            "interface_entries",
            "enum_entries",
        ):
            for entry in getattr(result, attribute):
                match = by_start.get((entry.declaring_type, entry.start_line))
                if match is None:
                    continue
                seen.add((entry.declaring_type, entry.start_line))
                if match["end_line"] < entry.end_line:
                    entry.end_line = match["end_line"]
                if not entry.namespace and match["namespace"]:
                    entry.namespace = match["namespace"]

        for declaration in scanned:
            key = (declaration["name"], declaration["start_line"])
            if key in seen:
                continue
            attribute = self._KIND_TO_ENTRIES.get(declaration["kind"])
            if attribute is None:
                continue
            getattr(result, attribute).append(
                IndexEntry(
                    namespace=declaration["namespace"],
                    declaring_type=declaration["name"],
                    method="",
                    symbol_name="",
                    entry_type="declaration",
                    file_path=file_path,
                    start_line=declaration["start_line"],
                    end_line=declaration["end_line"],
                    description=self._comment_above_line(
                        declaration["start_line"], context["source_lines"]
                    ),
                )
            )
            declared = getattr(result, self._KIND_TO_DECLARED[declaration["kind"]])
            declared.setdefault(declaration["name"], set()).add(
                (declaration["namespace"], "")
            )

        # --- 3: re-attribute members ---------------------------------------
        self._reattribute_members(scanned, result)

    def _comment_above_line(self, start_line: int, source_lines: List[str]) -> str:
        """`_get_preceding_comment` for a 1-indexed line rather than a node."""
        comment_lines = []
        current_line = start_line - 2
        while current_line >= 0 and source_lines[current_line].strip().startswith("["):
            current_line -= 1
        while current_line >= 0:
            line = source_lines[current_line].strip()
            if not line.startswith("//"):
                break
            comment_lines.insert(0, (line[3:] if line.startswith("///") else line[2:]).strip())
            current_line -= 1
        return self._clean_doc_comment(" ".join(comment_lines))

    def _reattribute_members(self, scanned: List[Dict], result: FileProcessingResult):
        """Point each member at the innermost declaration that contains it."""
        ordered = sorted(scanned, key=lambda d: (d["start_line"], -d["end_line"]))
        if not ordered:
            return

        def owner_of(line: int) -> Optional[Dict]:
            best: Optional[Dict] = None
            for declaration in ordered:
                if declaration["start_line"] > line:
                    break
                if declaration["end_line"] >= line:
                    # Later candidates start later, so they nest deeper.
                    best = declaration
            return best

        for attribute in (
            "method_entries",
            "field_entries",
            "property_entries",
            "event_entries",
            "constructor_entries",
            "enum_member_entries",
        ):
            for entry in getattr(result, attribute):
                declaration = owner_of(entry.start_line)
                if declaration is None:
                    continue
                entry.declaring_type = declaration["name"]
                if declaration["namespace"]:
                    entry.namespace = declaration["namespace"]

        for entry in result.signature_entries:
            declaration = owner_of(entry.start_line)
            if declaration is not None:
                entry.declaring_type = declaration["name"]
                if declaration["namespace"]:
                    entry.namespace = declaration["namespace"]

    def _recover_hierarchy(
        self, scanned: List[Dict], file_path: str, result: FileProcessingResult
    ):
        """Emit the hierarchy rows the dissolved declarations never produced.

        Runs in pass 2, where `declared_interfaces` covers the whole tree, so
        the base class can be told apart from the implemented interfaces.
        """
        have_classes = {
            (e.child_class, e.start_line) for e in result.class_hierarchy_entries
        }
        have_interfaces = {
            (e.child_interface, e.start_line)
            for e in result.interface_hierarchy_entries
        }
        have_impls = {
            (e.implementing_type, e.start_line)
            for e in result.interface_implementation_entries
        }

        for declaration in scanned:
            kind = declaration["kind"]
            if kind == "enum":
                continue

            name = declaration["name"]
            namespace = declaration["namespace"]
            start = declaration["start_line"]
            end = declaration["end_line"]
            bases = declaration["bases"]

            if kind == "interface":
                if (name, start) in have_interfaces or not bases:
                    continue
                for parent in bases:
                    parent_ns, parent_name = self._split_namespace_and_type(
                        self._resolve_type_namespace(parent, namespace)
                    )
                    result.interface_hierarchy_entries.append(
                        InterfaceHierarchyEntry(
                            child_namespace=namespace,
                            child_interface=name,
                            parent_namespace=parent_ns,
                            parent_interface=parent_name,
                            file_path=file_path,
                            start_line=start,
                            end_line=end,
                        )
                    )
                continue

            interfaces = bases
            if kind == "struct":
                # Structs cannot inherit, so every base is an interface and no
                # class-hierarchy row is emitted.
                pass
            else:
                if (name, start) in have_classes:
                    continue
                base_ns, base_name = "System", "Object"
                if bases:
                    first_ns, first_name = self._split_namespace_and_type(
                        self._resolve_type_namespace(bases[0], namespace)
                    )
                    first_base, _ = self._split_generic(first_name)
                    if first_base not in self.declared_interfaces:
                        base_ns, base_name = first_ns, first_name
                        interfaces = bases[1:]

                result.class_hierarchy_entries.append(
                    ClassHierarchyEntry(
                        child_namespace=namespace,
                        child_class=name,
                        parent_namespace=base_ns,
                        parent_class=base_name,
                        file_path=file_path,
                        start_line=start,
                        end_line=end,
                    )
                )

            if interfaces and (name, start) not in have_impls:
                result.interface_implementation_entries.append(
                    InterfaceImplementationEntry(
                        implementing_namespace=namespace,
                        implementing_type=name,
                        interfaces=INTERFACE_SEPARATOR.join(
                            self._resolve_interface_list(interfaces, namespace)
                        ),
                        file_path=file_path,
                        start_line=start,
                        end_line=end,
                    )
                )

    def _get_identifier_name(self, node: Node) -> Optional[str]:
        """Extract identifier name from a node"""
        # The grammar labels the declared name with the `name` field. Trust it
        # first: the positional scans below cannot tell a property's type from
        # its name, so `SharpDX.Direct3D11.Device DeviceInstance { get; }` used
        # to be recorded with the type in symbol_name and the name lost. The
        # same shape hit explicit interface implementations and any property
        # whose type is a plain identifier.
        named = node.child_by_field_name("name")
        if named is not None and named.text:
            return named.text.decode("utf-8")

        # For method/constructor declarations, we need the identifier right before the parameter list
        # (not the return type which comes first)
        if node.type in ("method_declaration", "constructor_declaration"):
            # Find the identifier that comes right before the parameter_list
            identifiers = []
            for child in node.children:
                if child.type == "identifier":
                    identifiers.append(child.text.decode("utf-8"))
                elif child.type == "parameter_list" and identifiers:
                    # The last identifier before parameter_list is the method name
                    return identifiers[-1]
            # Fallback: return last identifier if no parameter_list found
            if identifiers:
                return identifiers[-1]
        else:
            # For other node types, return first identifier as before
            for child in node.children:
                if child.type == "identifier":
                    return child.text.decode("utf-8")
                elif child.type == "qualified_name":
                    return child.text.decode("utf-8")
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
            return ""

        comment_lines = []
        current_line = start_line - 1

        # A doc comment sits above the attribute list, not below it, so walk
        # past any attributes first. Without this, every `[Flags]` enum and
        # every attribute-decorated type lost its documentation.
        while current_line >= 0 and source_lines[current_line].strip().startswith("["):
            current_line -= 1

        while current_line >= 0:
            line = source_lines[current_line].strip()

            if line.startswith("//"):
                # `///` is a doc comment, not a `//` comment with a stray
                # slash. Stripping only two characters left a leading `/` on
                # every doc line and the raw XML tags around it, which is what
                # produced descriptions reading `/ <summary> / Gets ... /`.
                text = line[3:] if line.startswith("///") else line[2:]
                comment_lines.insert(0, text.strip())
                current_line -= 1
            elif line.endswith("*/"):
                multi_line_parts = []
                while current_line >= 0:
                    line = source_lines[current_line].strip()
                    line = (
                        line.replace("/*", "")
                        .replace("*/", "")
                        .replace("*", "")
                        .strip()
                    )
                    if line:
                        multi_line_parts.insert(0, line)
                    if "/*" in source_lines[current_line]:
                        break
                    current_line -= 1
                comment_lines = multi_line_parts + comment_lines
                break
            elif not line:
                break
            else:
                break

        return self._clean_doc_comment(" ".join(comment_lines))

    # XML doc elements whose text is the description itself; the tags add
    # nothing once the text is flattened into a CSV cell.
    _DOC_TAG_RE = re.compile(r"</?(?:summary|remarks|para|value|returns)\s*/?>")
    _DOC_INLINE_RE = re.compile(r"<(?:see|seealso|paramref|typeparamref)\b[^>]*?"
                                r"(?:cref|name)\s*=\s*\"([^\"]*)\"[^>]*/?>")

    @classmethod
    def _clean_doc_comment(cls, text: str) -> str:
        """Flatten an XML doc comment into one readable sentence.

        Keeps the prose and the referenced names, drops the markup. Anything
        that is not recognized XML doc markup passes through untouched, so an
        ordinary `//` comment is unaffected.
        """
        if not text or "<" not in text:
            return text.strip()
        # `<see cref="T:VRage.Foo"/>` -> `VRage.Foo`
        text = cls._DOC_INLINE_RE.sub(lambda m: m.group(1).split(":")[-1], text)
        text = cls._DOC_TAG_RE.sub(" ", text)
        return re.sub(r"\s+", " ", text).strip()

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
                # The modifier node wraps a keyword child
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
                    # Normalize whitespace within the parameter list
                    raw = text.decode("utf-8")
                    return re.sub(r"\s+", " ", raw).strip()
        return ""

    # Punctuation and keyword tokens that appear inside a base_list but are not
    # types. Anything else is treated as a type node.
    _BASE_LIST_NOISE = frozenset({":", ",", "base_list", "comment"})

    def _extract_type_name(self, node: Node) -> Optional[str]:
        """Extract a type name from a type node, keeping generic arguments.

        Generic arguments used to be stripped here, which collapsed
        `IEnumerable<T>` and `IEnumerable` into one string and made every
        generic/non-generic pair look like a duplicate implementation.
        """
        text = node.text
        if not text:
            return None
        # Declarations can wrap across lines; normalize the whitespace so
        # `IDictionary<string,\n    int>` compares equal to the one-line form.
        return re.sub(r"\s+", " ", text.decode("utf-8")).strip()

    def _get_base_list_types(self, node: Node) -> List[str]:
        """Extract all type names from a base_list node.

        Accepts any non-punctuation child rather than a whitelist of three node
        types, so nullable, array and alias-qualified bases are not silently
        dropped.
        """
        types = []
        for child in node.children:
            if child.type in self._BASE_LIST_NOISE:
                continue
            type_name = self._extract_type_name(child)
            if type_name:
                types.append(type_name)
        return types

    @staticmethod
    def _split_generic(type_name: str) -> Tuple[str, str]:
        """`IEnumerable<T>` -> `("IEnumerable", "<T>")`; no generics -> `(name, "")`."""
        index = type_name.find("<")
        if index < 0:
            return type_name, ""
        return type_name[:index].strip(), type_name[index:]

    def _find_base_list(self, node: Node) -> Optional[Node]:
        """Find the base_list child node"""
        for child in node.children:
            if child.type == "base_list":
                return child
        return None

    def _resolve_type_namespace(self, type_name: str, current_namespace: str) -> str:
        """
        Attempt to resolve the namespace of a type.

        Returns the qualified name when the type is declared somewhere in the
        indexed tree, and the bare name when it is not.

        The old behaviour was to fall through to `current_namespace.TypeName`
        for anything unresolved. Because the BCL is not part of the indexed
        tree, that stamped the implementing type's own namespace onto every
        framework interface: `IEnumerator` implemented by a type in
        `VRage.Input` was recorded as `VRage.Input.IEnumerator`, a type that
        does not exist. Returning the bare name says "declared elsewhere",
        which is both true and what consumers can act on.
        """
        base, args = self._split_generic(type_name)

        # If already qualified (contains a dot), return as-is
        if "." in base:
            return type_name

        # Check if it's in the current namespace
        full_name = f"{current_namespace}.{base}" if current_namespace else base

        # Try to match against known types in declared sets
        for declared in (
            self.declared_interfaces,
            self.declared_classes,
            self.declared_structs,
        ):
            if base not in declared:
                continue
            locations = declared[base]
            for ns, _ in locations:
                if ns == current_namespace:
                    return full_name + args
            if locations:
                ns, _ = next(iter(locations))
                return (f"{ns}.{base}" if ns else base) + args

        # Not declared anywhere in the indexed tree: almost always a BCL or
        # third-party type. Report the bare name rather than inventing one.
        return base + args

    def _split_namespace_and_type(self, fully_qualified: str) -> Tuple[str, str]:
        """Split a fully-qualified type name into namespace and type name.

        Generic arguments are set aside first, so a dotted type *inside* the
        argument list cannot be mistaken for the namespace separator:
        `Dictionary<string, My.Ns.Foo>` splits as `("", "Dictionary<...>")`,
        not `("Dictionary<string, My.Ns", "Foo>")`.
        """
        base, args = self._split_generic(fully_qualified)
        if "." not in base:
            return ("", base + args)
        namespace, name = base.rsplit(".", 1)
        return (namespace, name + args)

    def _extract_method_signature(
        self, node: Node, source_lines: List[str]
    ) -> Tuple[str, int, int]:
        """
        Extract the method signature (everything before the body).
        Returns (signature_text, start_line, end_line) where lines are 1-indexed.
        Handles abstract methods (no body), inline => methods, and block {...} methods.
        """
        start_line = node.start_point[0]  # 0-indexed
        start_col = node.start_point[1]

        # Find the body node - could be 'block' ({...}) or 'arrow_expression_clause' (=>)
        body_node = None
        semicolon_pos = None
        for child in node.children:
            if child.type == "block":
                body_node = child
                break
            elif child.type == "arrow_expression_clause":
                body_node = child
                break
            elif child.type == ";":
                # Abstract method or interface method (no body, ends with semicolon)
                semicolon_pos = (child.start_point[0], child.start_point[1])

        if body_node:
            # Signature ends just before the body
            end_line = body_node.start_point[0]  # 0-indexed
            end_col = body_node.start_point[1]
        elif semicolon_pos:
            # Abstract method - signature includes up to and including the semicolon position
            end_line = semicolon_pos[0]
            end_col = semicolon_pos[1] + 1  # Include the semicolon
        else:
            # Fallback: use the whole first line of the method
            end_line = start_line
            end_col = (
                len(source_lines[start_line]) if start_line < len(source_lines) else 0
            )

        # Extract signature text from source lines
        sig_parts = []
        for line_idx in range(start_line, end_line + 1):
            if line_idx >= len(source_lines):
                break
            line = source_lines[line_idx]
            if line_idx == start_line and line_idx == end_line:
                # Single line signature
                sig_parts.append(line[start_col:end_col])
            elif line_idx == start_line:
                sig_parts.append(line[start_col:])
            elif line_idx == end_line:
                sig_parts.append(line[:end_col])
            else:
                sig_parts.append(line)

        # Join and normalize whitespace
        raw_signature = " ".join(sig_parts)
        # Normalize: replace multiple whitespace with single space, strip
        normalized = re.sub(r"\s+", " ", raw_signature).strip()

        # Calculate 1-indexed end line (inclusive)
        # If the body/semicolon is on a different line than the signature start,
        # the signature ends on the line before the body (end_line in 0-indexed
        # equals the 1-indexed last signature line due to the off-by-one)
        if end_line > start_line:
            sig_end_line = end_line  # 0-indexed body line = 1-indexed signature end
        else:
            sig_end_line = end_line + 1  # Same line, convert 0-indexed to 1-indexed

        return (normalized, start_line + 1, sig_end_line)

    def _process_file_scoped_namespace(
        self, node: Node, context: Dict, result: FileProcessingResult
    ):
        """Process file-scoped namespace declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context["namespace"] = name
        result.declared_namespaces.add(name)

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=name,
            declaring_type="",
            method="",
            symbol_name="",
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
        )
        result.namespace_entries.append(entry)

    def _process_namespace(
        self, node: Node, context: Dict, result: FileProcessingResult
    ):
        """Process namespace declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        full_namespace = self._build_namespace(context["namespace"], name)
        context["namespace"] = full_namespace
        result.declared_namespaces.add(full_namespace)

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=full_namespace,
            declaring_type="",
            method="",
            symbol_name="",
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
        )
        result.namespace_entries.append(entry)

    def _process_interface(
        self, node: Node, context: Dict, result: FileProcessingResult
    ):
        """Process interface declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context["declaring_type"] = name

        if name not in result.declared_interfaces:
            result.declared_interfaces[name] = set()
        result.declared_interfaces[name].add((context["namespace"], ""))

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=context["namespace"],
            declaring_type=name,
            method="",
            symbol_name="",
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
        )
        result.interface_entries.append(entry)

        # Note: interface hierarchy extraction is done in Pass 2
        # (_process_type_hierarchy) where declared_interfaces is populated

    def _resolve_interface_list(
        self, interfaces: List[str], current_namespace: str
    ) -> List[str]:
        """Resolve each implemented interface and drop repeats, keeping order.

        Repeats used to be common: generic arguments were stripped before this
        point, so `IEnumerable<T>` and `IEnumerable` both arrived as
        `IEnumerable` and were written twice.
        """
        resolved: List[str] = []
        seen: Set[str] = set()
        for iface in interfaces:
            fqn = self._resolve_type_namespace(iface, current_namespace)
            if fqn not in seen:
                seen.add(fqn)
                resolved.append(fqn)
        return resolved

    def _process_type_hierarchy(
        self, node: Node, context: Dict, result: FileProcessingResult
    ):
        """Process base types for class/struct/record/interface declarations.

        Called during Pass 2 when self.declared_interfaces is populated
        with all interface declarations from the entire codebase.
        """
        name = self._get_identifier_name(node)
        if not name:
            return

        base_list = self._find_base_list(node)
        base_types = self._get_base_list_types(base_list) if base_list else []

        if node.type == "interface_declaration":
            # All items in an interface base list are parent interfaces.
            # A root interface with no base list simply produces no rows.
            for parent_type in base_types:
                parent_fqn = self._resolve_type_namespace(
                    parent_type, context["namespace"]
                )
                parent_ns, parent_name = self._split_namespace_and_type(parent_fqn)

                hier_entry = InterfaceHierarchyEntry(
                    child_namespace=context["namespace"],
                    child_interface=name,
                    parent_namespace=parent_ns,
                    parent_interface=parent_name,
                    file_path=context["file_path"],
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                )
                result.interface_hierarchy_entries.append(hier_entry)

        elif node.type == "struct_declaration":
            # Structs can only implement interfaces (no struct inheritance).
            # A struct with no base list implements nothing, so emit no row.
            if base_types:
                interface_fqns = self._resolve_interface_list(
                    base_types, context["namespace"]
                )
                impl_entry = InterfaceImplementationEntry(
                    implementing_namespace=context["namespace"],
                    implementing_type=name,
                    interfaces=INTERFACE_SEPARATOR.join(interface_fqns),
                    file_path=context["file_path"],
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                )
                result.interface_implementation_entries.append(impl_entry)

        else:
            # class_declaration or record_declaration.
            # Every class has a base class: when none is written explicitly, or
            # the base list contains only interfaces, the base is the implicit
            # System.Object. We ALWAYS emit a ClassHierarchyEntry so that root
            # classes are not missing from the hierarchy index (previously a
            # class with no explicit class base got no row at all, hiding it
            # from every consumer that enumerates types from the hierarchy).
            base_class_ns, base_class_name = "System", "Object"
            interfaces = base_types
            if base_types:
                first_type = base_types[0]
                first_fqn = self._resolve_type_namespace(
                    first_type, context["namespace"]
                )
                first_ns, first_name = self._split_namespace_and_type(first_fqn)

                # declared_interfaces is keyed by simple name without generic
                # arguments, so strip them before the lookup.
                first_base, _ = self._split_generic(first_name)
                if first_base not in self.declared_interfaces:
                    # First item is the base class; the rest are interfaces.
                    base_class_ns, base_class_name = first_ns, first_name
                    interfaces = base_types[1:]

            hier_entry = ClassHierarchyEntry(
                child_namespace=context["namespace"],
                child_class=name,
                parent_namespace=base_class_ns,
                parent_class=base_class_name,
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
            )
            result.class_hierarchy_entries.append(hier_entry)

            # Process implemented interfaces.
            if interfaces:
                interface_fqns = self._resolve_interface_list(
                    interfaces, context["namespace"]
                )
                impl_entry = InterfaceImplementationEntry(
                    implementing_namespace=context["namespace"],
                    implementing_type=name,
                    interfaces=INTERFACE_SEPARATOR.join(interface_fqns),
                    file_path=context["file_path"],
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                )
                result.interface_implementation_entries.append(impl_entry)

    def _process_class(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process class/record declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context["declaring_type"] = name

        if name not in result.declared_classes:
            result.declared_classes[name] = set()
        result.declared_classes[name].add((context["namespace"], ""))

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=context["namespace"],
            declaring_type=name,
            method="",
            symbol_name="",
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
        )
        result.class_entries.append(entry)

        # Note: hierarchy/implementation extraction is done in Pass 2
        # (_process_type_hierarchy) where declared_interfaces is populated

    def _process_struct(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process struct declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context["declaring_type"] = name

        if name not in result.declared_structs:
            result.declared_structs[name] = set()
        result.declared_structs[name].add((context["namespace"], ""))

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=context["namespace"],
            declaring_type=name,
            method="",
            symbol_name="",
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
        )
        result.struct_entries.append(entry)

        # Note: interface implementation extraction is done in Pass 2
        # (_process_type_hierarchy) where declared_interfaces is populated

    def _process_enum(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process enum declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        context["declaring_type"] = name

        if name not in result.declared_enums:
            result.declared_enums[name] = set()
        result.declared_enums[name].add((context["namespace"], ""))

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=context["namespace"],
            declaring_type=name,
            method="",
            symbol_name="",
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
        )
        result.enum_entries.append(entry)

        self._process_enum_members(node, context, result, name)

    def _process_enum_members(
        self,
        node: Node,
        context: Dict,
        result: FileProcessingResult,
        enum_name: str,
    ):
        """Emit one row per enum member.

        Enum members were previously indexed nowhere: `field_declarations.csv`
        holds no rows for enum source files, so every consumer could see that
        an enum existed and nothing about what was in it. The values are the
        only thing an enum really has.

        Column mapping for `enum_member_declarations.csv`:
          declaring_type  the enum
          symbol_name     the member name
          member_type     the enum's underlying type (`int` when not declared)
          params          the explicit initializer as written, or empty
          description     the member's own doc comment
        """
        underlying = ""
        base_list = self._find_base_list(node)
        if base_list is not None:
            base_types = self._get_base_list_types(base_list)
            if base_types:
                underlying = base_types[0]

        body = None
        for child in node.children:
            if child.type == "enum_member_declaration_list":
                body = child
                break
        if body is None:
            return

        for member in body.children:
            if member.type != "enum_member_declaration":
                continue
            member_name = self._get_identifier_name(member)
            if not member_name:
                continue

            # The initializer is whatever follows `=`. Keep it verbatim so
            # `0x10` and `A | B` survive as written rather than as a number.
            value = ""
            seen_equals = False
            parts: List[str] = []
            for part in member.children:
                if part.type == "=":
                    seen_equals = True
                    continue
                if seen_equals and part.text:
                    parts.append(part.text.decode("utf-8"))
            if parts:
                value = re.sub(r"\s+", " ", " ".join(parts)).strip()

            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=enum_name,
                method="",
                symbol_name=member_name,
                entry_type="declaration",
                file_path=context["file_path"],
                start_line=member.start_point[0] + 1,
                end_line=member.end_point[0] + 1,
                description=self._get_preceding_comment(
                    member, context["source_lines"]
                ),
                member_type=underlying,
                params=value,
            )
            result.enum_member_entries.append(entry)

    def _process_method(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process method or constructor declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        is_constructor = node.type == "constructor_declaration"

        context["method"] = name

        if name not in result.declared_methods:
            result.declared_methods[name] = set()
        result.declared_methods[name].add(
            (context["namespace"], context["declaring_type"])
        )

        if is_constructor:
            if name not in result.declared_constructors:
                result.declared_constructors[name] = set()
            result.declared_constructors[name].add(
                (context["namespace"], context["declaring_type"])
            )

        access, modifiers = self._extract_modifiers(node)
        params_text = self._extract_params_text(node)

        # Extract return type (methods only — constructors have no return type)
        return_type = ""
        if not is_constructor:
            # The return type node has field name [returns] and comes before the method name
            # In the tree: modifier* return_type method_name parameter_list body
            found_type = False
            for child in node.children:
                if child.type == "modifier":
                    continue
                if not found_type and child.type != "identifier":
                    # First non-modifier, non-identifier child is the return type
                    return_type = self._extract_full_type_text(child)
                    found_type = True
                elif child.type == "identifier":
                    break  # We've hit the method name, stop

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=context["namespace"],
            declaring_type=context["declaring_type"],
            method=name,
            symbol_name="",
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
            access=access,
            modifiers=modifiers,
            member_type=return_type,
            params=params_text,
        )

        if is_constructor:
            result.constructor_entries.append(entry)
        else:
            result.method_entries.append(entry)

        # Also create a signature entry
        signature_text, sig_start, sig_end = self._extract_method_signature(
            node, context["source_lines"]
        )
        sig_entry = SignatureEntry(
            namespace=context["namespace"],
            declaring_type=context["declaring_type"],
            method_name=name,
            signature=signature_text,
            file_path=context["file_path"],
            start_line=sig_start,
            end_line=sig_end,
            description=description,
        )
        result.signature_entries.append(sig_entry)

    def _process_field(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process field (member variable) declaration"""
        access, modifiers = self._extract_modifiers(node)

        for child in node.children:
            if child.type == "variable_declaration":
                # Extract the type from the variable_declaration
                type_text = ""
                for vc in child.children:
                    if vc.type not in ("variable_declarator", ",", ";"):
                        # This is the type node
                        type_text = self._extract_full_type_text(vc)
                        break
                for declarator in child.children:
                    if declarator.type == "variable_declarator":
                        name = self._get_identifier_name(declarator)
                        if name:
                            description = self._get_preceding_comment(
                                node, context["source_lines"]
                            )

                            entry = IndexEntry(
                                namespace=context["namespace"],
                                declaring_type=context["declaring_type"],
                                method="",
                                symbol_name=name,
                                entry_type="declaration",
                                file_path=context["file_path"],
                                start_line=node.start_point[0] + 1,
                                end_line=node.end_point[0] + 1,
                                description=description,
                                access=access,
                                modifiers=modifiers,
                                member_type=type_text,
                            )
                            result.field_entries.append(entry)

    def _process_property(
        self, node: Node, context: Dict, result: FileProcessingResult
    ):
        """Process property declaration"""
        name = self._get_identifier_name(node)
        if not name:
            return

        if name not in result.declared_properties:
            result.declared_properties[name] = set()
        result.declared_properties[name].add(
            (context["namespace"], context["declaring_type"])
        )

        access, modifiers = self._extract_modifiers(node)

        # The grammar labels the property type with the `type` field. The
        # positional fallback below skips `identifier` nodes, so it could not
        # see a property whose type is a plain user type name and left
        # member_type empty for 34% of properties.
        type_text = ""
        type_node = node.child_by_field_name("type")
        if type_node is not None:
            type_text = self._extract_full_type_text(type_node)
        else:
            for child in node.children:
                if child.type not in (
                    "modifier",
                    "identifier",
                    "accessor_list",
                    "arrow_expression_clause",
                    "explicit_interface_specifier",
                    "=",
                    ";",
                    "{",
                    "}",
                ):
                    # This should be the type node
                    type_text = self._extract_full_type_text(child)
                    break

        description = self._get_preceding_comment(node, context["source_lines"])

        entry = IndexEntry(
            namespace=context["namespace"],
            declaring_type=context["declaring_type"],
            method="",
            symbol_name=name,
            entry_type="declaration",
            file_path=context["file_path"],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            description=description,
            access=access,
            modifiers=modifiers,
            member_type=type_text,
        )
        result.property_entries.append(entry)

    def _process_event(self, node: Node, context: Dict, result: FileProcessingResult):
        """Process event declaration (event_field_declaration or event_declaration)"""
        access, modifiers = self._extract_modifiers(node)

        if node.type == "event_field_declaration":
            # event_field_declaration has: modifier* event variable_declaration ;
            # The type and name are inside variable_declaration
            for child in node.children:
                if child.type == "variable_declaration":
                    type_text = ""
                    for vc in child.children:
                        if vc.type not in ("variable_declarator", ",", ";"):
                            # This is the type node
                            type_text = self._extract_full_type_text(vc)
                    for vc in child.children:
                        if vc.type == "variable_declarator":
                            name = self._get_identifier_name(vc)
                            if name:
                                if name not in result.declared_events:
                                    result.declared_events[name] = set()
                                result.declared_events[name].add(
                                    (context["namespace"], context["declaring_type"])
                                )
                                description = self._get_preceding_comment(
                                    node, context["source_lines"]
                                )
                                entry = IndexEntry(
                                    namespace=context["namespace"],
                                    declaring_type=context["declaring_type"],
                                    method="",
                                    symbol_name=name,
                                    entry_type="declaration",
                                    file_path=context["file_path"],
                                    start_line=node.start_point[0] + 1,
                                    end_line=node.end_point[0] + 1,
                                    description=description,
                                    access=access,
                                    modifiers=modifiers,
                                    member_type=type_text,
                                )
                                result.event_entries.append(entry)
        else:
            # event_declaration has: modifier* event type name accessor_list
            # (event with explicit add/remove accessors)
            name = self._get_identifier_name(node)
            if not name:
                return

            if name not in result.declared_events:
                result.declared_events[name] = set()
            result.declared_events[name].add(
                (context["namespace"], context["declaring_type"])
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
            description = self._get_preceding_comment(node, context["source_lines"])
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=context["declaring_type"],
                method="",
                symbol_name=name,
                entry_type="declaration",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description=description,
                access=access,
                modifiers=modifiers,
                member_type=type_text,
            )
            result.event_entries.append(entry)

    def _process_identifier_usage(
        self, node: Node, context: Dict, result: FileProcessingResult
    ):
        """Process identifier usage (not a declaration)"""
        parent = node.parent
        if not parent:
            return

        declaration_types = {
            "namespace_declaration",
            "interface_declaration",
            "class_declaration",
            "struct_declaration",
            "record_declaration",
            "enum_declaration",
            "enum_member_declaration",
            "method_declaration",
            "constructor_declaration",
            "field_declaration",
            "property_declaration",
            "variable_declaration",
            "variable_declarator",
            "parameter",
            "type_parameter",
            "using_directive",
            "qualified_name",
            "member_access_expression",
        }

        if parent.type in declaration_types:
            return

        grandparent = parent.parent
        if grandparent and grandparent.type in declaration_types:
            return

        name = node.text.decode("utf-8")
        added = False

        if name in self.declared_namespaces:
            entry = IndexEntry(
                namespace=name,
                declaring_type="",
                method="",
                symbol_name="",
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.namespace_entries.append(entry)
            added = True

        if name in self.declared_interfaces:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=name,
                method=context["method"],
                symbol_name="",
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.interface_entries.append(entry)
            added = True

        if name in self.declared_classes:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=name,
                method=context["method"],
                symbol_name="",
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.class_entries.append(entry)
            added = True

        if name in self.declared_structs:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=name,
                method=context["method"],
                symbol_name="",
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.struct_entries.append(entry)
            added = True

        if name in self.declared_enums:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=name,
                method=context["method"],
                symbol_name="",
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.enum_entries.append(entry)
            added = True

        if name in self.declared_methods:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=context["declaring_type"],
                method=name,
                symbol_name="",
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
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
                    namespace=context["namespace"],
                    declaring_type=context["declaring_type"],
                    method=name,
                    symbol_name="",
                    entry_type="usage",
                    file_path=context["file_path"],
                    start_line=node.start_point[0] + 1,
                    end_line=node.end_point[0] + 1,
                    description="",
                )
                result.constructor_entries.append(entry)
                added = True

        if name in self.declared_properties:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=context["declaring_type"],
                method=context["method"],
                symbol_name=name,
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.property_entries.append(entry)
            added = True

        if name in self.declared_events:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=context["declaring_type"],
                method=context["method"],
                symbol_name=name,
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.event_entries.append(entry)
            added = True

        if not added:
            entry = IndexEntry(
                namespace=context["namespace"],
                declaring_type=context["declaring_type"],
                method=context["method"],
                symbol_name=name,
                entry_type="usage",
                file_path=context["file_path"],
                start_line=node.start_point[0] + 1,
                end_line=node.end_point[0] + 1,
                description="",
            )
            result.field_entries.append(entry)


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
        self.enum_member_index: List[IndexEntry] = []
        self.method_index: List[IndexEntry] = []
        self.field_index: List[IndexEntry] = []
        self.property_index: List[IndexEntry] = []
        self.event_index: List[IndexEntry] = []
        self.constructor_index: List[IndexEntry] = []
        self.signature_index: List[SignatureEntry] = []

        # Hierarchy indices
        self.class_hierarchy_index: List[ClassHierarchyEntry] = []
        self.interface_hierarchy_index: List[InterfaceHierarchyEntry] = []
        self.interface_implementation_index: List[InterfaceImplementationEntry] = []

        # Track declared names for each category to detect usages
        self.declared_namespaces: Set[str] = set()
        self.declared_interfaces: Dict[str, Set[tuple]] = {}
        self.declared_classes: Dict[str, Set[tuple]] = {}
        self.declared_structs: Dict[str, Set[tuple]] = {}
        self.declared_enums: Dict[str, Set[tuple]] = {}
        self.declared_methods: Dict[str, Set[tuple]] = {}
        self.declared_properties: Dict[str, Set[tuple]] = {}
        self.declared_events: Dict[str, Set[tuple]] = {}
        self.declared_constructors: Dict[str, Set[tuple]] = {}

        # Number of parallel workers (2x CPU cores)
        self.num_workers = cpu_count() * 2

    @staticmethod
    def _create_batches(files: List[Path], batch_size: int) -> List[List[Path]]:
        """Split files into batches of specified size"""
        batches = []
        for i in range(0, len(files), batch_size):
            batches.append(files[i : i + batch_size])
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
                self.enum_member_index.extend(result.enum_member_entries)
                self.method_index.extend(result.method_entries)
                self.field_index.extend(result.field_entries)
                self.property_index.extend(result.property_entries)
                self.event_index.extend(result.event_entries)
                self.constructor_index.extend(result.constructor_entries)
                self.signature_index.extend(result.signature_entries)
                self.class_hierarchy_index.extend(result.class_hierarchy_entries)
                self.interface_hierarchy_index.extend(
                    result.interface_hierarchy_entries
                )
                self.interface_implementation_index.extend(
                    result.interface_implementation_entries
                )

    def _merge_batch_declarations(
        self, batch_results: List[List[FileProcessingResult]]
    ):
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

    def index_directory(self):
        """Recursively index all C# files in the directory using parallel processing"""
        cs_files = list(self.root_path.rglob("*.cs"))
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
            "namespaces": self.declared_namespaces,
            "interfaces": self.declared_interfaces,
            "classes": self.declared_classes,
            "structs": self.declared_structs,
            "enums": self.declared_enums,
            "methods": self.declared_methods,
            "properties": self.declared_properties,
            "events": self.declared_events,
            "constructors": self.declared_constructors,
        }

        # Second pass: collect usages in parallel
        print("\nPass 2: Collecting usages...")
        pass2_args = [
            (batch, root_path_str, True, shared_declarations) for batch in batches
        ]

        with Pool(processes=self.num_workers) as pool:
            pass2_results = list(pool.imap_unordered(_process_batch_worker, pass2_args))

        # Merge usage results
        self._merge_batch_results(pass2_results)
        print(f"Completed pass 2: {total_files} files.")

    def write_indices(self, output_dir: Path):
        """Write all indices to CSV files - declarations and usages in separate files"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Split entries into declarations and usages for each category
        def split_entries(entries):
            declarations = [e for e in entries if e.entry_type == "declaration"]
            usages = [e for e in entries if e.entry_type == "usage"]
            return declarations, usages

        # Define categories with their indices (singular form for filename)
        categories = [
            ("namespace", self.namespace_index),
            ("interface", self.interface_index),
            ("class", self.class_index),
            ("struct", self.struct_index),
            ("enum", self.enum_index),
            ("method", self.method_index),
            ("field", self.field_index),
            ("property", self.property_index),
            ("event", self.event_index),
            ("constructor", self.constructor_index),
        ]

        total_declarations = 0
        total_usages = 0

        for category_name, index_data in categories:
            declarations, usages = split_entries(index_data)
            total_declarations += len(declarations)
            total_usages += len(usages)

            # Sort function for entries
            def sort_key(e):
                return (
                    e.namespace,
                    e.declaring_type,
                    e.method,
                    e.symbol_name,
                    e.file_path,
                    e.start_line,
                    e.end_line,
                )

            sorted_declarations = sorted(declarations, key=sort_key)
            sorted_usages = sorted(usages, key=sort_key)

            # Write declarations file
            decl_filename = f"{category_name}_declarations.csv"
            decl_path = output_dir / decl_filename
            print(
                f"Writing {len(sorted_declarations)} declaration entries to {decl_path}..."
            )

            with open(decl_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(IndexEntry.csv_header())
                for entry in sorted_declarations:
                    writer.writerow(entry.to_csv_row())

            # Write usages file
            usage_filename = f"{category_name}_usages.csv"
            usage_path = output_dir / usage_filename
            print(f"Writing {len(sorted_usages)} usage entries to {usage_path}...")

            with open(usage_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(IndexEntry.csv_header())
                for entry in sorted_usages:
                    writer.writerow(entry.to_csv_row())

        # Enum members. Written by a dedicated block rather than added to
        # `categories` above, because enum members have no usage form and an
        # empty enum_member_usages.csv would only mislead.
        def member_sort_key(e):
            return (e.namespace, e.declaring_type, e.file_path, e.start_line)

        sorted_enum_members = sorted(self.enum_member_index, key=member_sort_key)
        enum_member_path = output_dir / "enum_member_declarations.csv"
        print(
            f"Writing {len(sorted_enum_members)} enum member entries to {enum_member_path}..."
        )
        total_declarations += len(sorted_enum_members)

        with open(enum_member_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(IndexEntry.csv_header())
            for entry in sorted_enum_members:
                writer.writerow(entry.to_csv_row())

        # Write method_signatures.csv (different column structure)
        def sig_sort_key(e):
            return (
                e.namespace,
                e.declaring_type,
                e.method_name,
                e.file_path,
                e.start_line,
                e.end_line,
            )

        sorted_signatures = sorted(self.signature_index, key=sig_sort_key)
        sig_filename = "method_signatures.csv"
        sig_path = output_dir / sig_filename
        print(f"Writing {len(sorted_signatures)} signature entries to {sig_path}...")

        with open(sig_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(SignatureEntry.csv_header())
            for entry in sorted_signatures:
                writer.writerow(entry.to_csv_row())

        # Write hierarchy CSV files
        def hier_sort_key_class(e):
            return (
                e.child_namespace,
                e.child_class,
                e.parent_namespace,
                e.parent_class,
            )

        def hier_sort_key_interface(e):
            return (
                e.child_namespace,
                e.child_interface,
                e.parent_namespace,
                e.parent_interface,
            )

        def impl_sort_key(e):
            return (e.implementing_namespace, e.implementing_type, e.interfaces)

        # Class hierarchy
        sorted_class_hierarchy = sorted(
            self.class_hierarchy_index, key=hier_sort_key_class
        )
        class_hier_path = output_dir / "class_hierarchy.csv"
        print(
            f"Writing {len(sorted_class_hierarchy)} class hierarchy entries to {class_hier_path}..."
        )

        with open(class_hier_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(ClassHierarchyEntry.csv_header())
            for entry in sorted_class_hierarchy:
                writer.writerow(entry.to_csv_row())

        # Interface hierarchy
        sorted_interface_hierarchy = sorted(
            self.interface_hierarchy_index, key=hier_sort_key_interface
        )
        interface_hier_path = output_dir / "interface_hierarchy.csv"
        print(
            f"Writing {len(sorted_interface_hierarchy)} interface hierarchy entries to {interface_hier_path}..."
        )

        with open(interface_hier_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(InterfaceHierarchyEntry.csv_header())
            for entry in sorted_interface_hierarchy:
                writer.writerow(entry.to_csv_row())

        # Interface implementations
        sorted_implementations = sorted(
            self.interface_implementation_index, key=impl_sort_key
        )
        impl_path = output_dir / "interface_implementation.csv"
        print(
            f"Writing {len(sorted_implementations)} interface implementation entries to {impl_path}..."
        )

        with open(impl_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(InterfaceImplementationEntry.csv_header())
            for entry in sorted_implementations:
                writer.writerow(entry.to_csv_row())

        # Generate tree text files
        print("\nGenerating hierarchy tree visualizations...")

        from hierarchy_tree import build_class_tree, build_interface_tree

        # Class hierarchy tree
        if sorted_class_hierarchy:
            class_tree_data = [
                (e.child_namespace, e.child_class, e.parent_namespace, e.parent_class)
                for e in sorted_class_hierarchy
            ]
            class_tree_text = build_class_tree(class_tree_data)
            class_tree_path = output_dir / "class_hierarchy.txt"
            with open(class_tree_path, "w", encoding="utf-8") as f:
                f.write(class_tree_text)
            print(f"Written class hierarchy tree to {class_tree_path}")

        # Interface hierarchy tree
        if sorted_interface_hierarchy:
            interface_tree_data = [
                (
                    e.child_namespace,
                    e.child_interface,
                    e.parent_namespace,
                    e.parent_interface,
                )
                for e in sorted_interface_hierarchy
            ]
            interface_tree_text = build_interface_tree(interface_tree_data)
            interface_tree_path = output_dir / "interface_hierarchy.txt"
            with open(interface_tree_path, "w", encoding="utf-8") as f:
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


if __name__ == "__main__":
    main()
