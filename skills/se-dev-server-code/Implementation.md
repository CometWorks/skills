# Code Search Implementation Details

Technical documentation for contributors and those working on the skill itself.

## Index File Formats

All CSV files are located in `CodeIndex/` after preparation.

### Standard Index Files

Most index files use this column structure:

```csv
namespace,declaring_type,method,symbol_name,type,file_path,start_line,end_line,description,access,modifiers,member_type,params
```

#### Column Descriptions

- `namespace` - The namespace containing the symbol
- `declaring_type` - The class/struct/interface containing the symbol
- `method` - The method containing the symbol (empty for type-level declarations)
- `symbol_name` - Field/property/event name (for member indices)
- `type` - Either `declaration` or `usage`
- `file_path` - Relative path from `Decompiled/` folder
- `start_line`, `end_line` - Line range in source file (1-indexed, inclusive)
- `description` - XML doc comment summary (for declarations only)
- `access` - Access modifier: `public`, `private`, `protected`, `internal`, etc. (member declarations only)
- `modifiers` - Other modifiers: `static`, `virtual`, `override`, `abstract`, `readonly`, etc. (member declarations only)
- `member_type` - Return type (methods), field/property/event type (member declarations only)
- `params` - Parameter list including parentheses, e.g. `(int x, string name)` (methods/constructors only)

#### Files Using This Format

| Index File | Contains |
|------------|----------|
| `namespace_declarations.csv` | Namespace declarations |
| `namespace_usages.csv` | Namespace references |
| `interface_declarations.csv` | Interface declarations |
| `interface_usages.csv` | Interface references |
| `class_declarations.csv` | Class declarations |
| `class_usages.csv` | Class references |
| `struct_declarations.csv` | Struct declarations |
| `struct_usages.csv` | Struct references |
| `enum_declarations.csv` | Enum declarations |
| `enum_usages.csv` | Enum references |
| `method_declarations.csv` | Method declarations |
| `method_usages.csv` | Method call sites |
| `field_declarations.csv` | Field declarations |
| `field_usages.csv` | Field references |
| `property_declarations.csv` | Property declarations |
| `property_usages.csv` | Property references |
| `event_declarations.csv` | Event declarations |
| `event_usages.csv` | Event references |
| `constructor_declarations.csv` | Constructor declarations |
| `constructor_usages.csv` | Constructor references |

**Note:** The `access`, `modifiers`, `member_type`, and `params` columns are populated for member declarations (fields, properties, events, methods, constructors) and empty for type/namespace declarations and all usage entries.

### Method Signatures CSV

**File:** `method_signatures.csv`

**Different structure:**

```csv
namespace,declaring_type,method_name,signature,file_path,start_line,end_line,description
```

#### Column Descriptions

- `namespace` - Full namespace of the declaring class
- `declaring_type` - Class name (for inner classes: `ParentClass.ChildClass`)
- `method_name` - The method name
- `signature` - Full method signature on a single line (whitespace normalized)
- `file_path` - Relative path from `Decompiled/` folder
- `start_line`, `end_line` - Line range of signature only (not whole method body)
- `description` - XML doc comment before the method

**Includes:** Abstract methods, inline `=>` methods, and block `{...}` methods.

**Excludes:** Property getters/setters (indexed in field declarations).

### Class Hierarchy CSV

**File:** `class_hierarchy.csv`

Tracks class-to-class inheritance (base classes only).

```csv
child_namespace,child_class,parent_namespace,parent_class,file_path,start_line,end_line
```

- `child_namespace` - Namespace of the child class
- `child_class` - Name of the child class
- `parent_namespace` - Namespace of the parent/base class
- `parent_class` - Name of the parent/base class
- `file_path` - Source file containing the child class declaration
- `start_line`, `end_line` - Location of the child class declaration

**Note:** Only classes are indexed (not structs, as structs cannot inherit from classes).

### Interface Hierarchy CSV

**File:** `interface_hierarchy.csv`

Tracks interface-to-interface inheritance (interfaces extending other interfaces).

```csv
child_namespace,child_interface,parent_namespace,parent_interface,file_path,start_line,end_line
```

- `child_namespace` - Namespace of the child interface
- `child_interface` - Name of the child interface
- `parent_namespace` - Namespace of the parent interface
- `parent_interface` - Name of the parent interface
- `file_path` - Source file containing the child interface declaration
- `start_line`, `end_line` - Location of the child interface declaration

### Interface Implementation CSV

**File:** `interface_implementation.csv`

Tracks which classes/structs implement which interfaces.

```csv
implementing_namespace,implementing_type,interfaces,file_path,start_line,end_line
```

- `implementing_namespace` - Namespace of the implementing class/struct
- `implementing_type` - Name of the class/struct
- `interfaces` - **Comma-separated** list of fully-qualified interface names (format: `Namespace.InterfaceName`)
- `file_path` - Source file containing the class/struct declaration
- `start_line`, `end_line` - Location of the class/struct declaration

**Example row:**
```csv
Sandbox.Game,MyTerminalBlock,"VRage.Game.ModAPI.IMyTerminalBlock,Sandbox.ModAPI.IMyFunctionalBlock",Sandbox.Game/Sandbox/Game/MyTerminalBlock.cs,100,500
```

## Tree Visualization Files

### Class Hierarchy Tree

**File:** `class_hierarchy.txt`

Tree-style visualization of complete class hierarchy, similar to the `tree` command.

**Format:**
```
System.Object
├── VRage.Game.Entity.MyEntityBase
│   ├── VRage.Game.Entity.MyEntity
│   │   ├── Sandbox.Game.MyGrid
│   │   ├── Sandbox.Game.MyCharacter
│   │   └── Sandbox.Game.MyProjectile
│   └── VRage.Game.Entity.MySimpleEntity
└── VRage.Collections.MyList
    └── Sandbox.Game.MySpecializedList
```

**Features:**
- Shows complete class inheritance tree
- Roots start with classes that have no parent (inherit from `System.Object`)
- Uses box-drawing characters (`├──`, `└──`, `│`)
- Sorted alphabetically at each level
- Fully-qualified type names (namespace.class)

### Interface Hierarchy Tree

**File:** `interface_hierarchy.txt`

Tree-style visualization of complete interface hierarchy.

**Format:**
```
VRage.ModAPI.IMyEntity
├── VRage.Game.ModAPI.IMyCubeBlock
│   ├── VRage.Game.ModAPI.IMyTerminalBlock
│   │   ├── VRage.Game.ModAPI.IMyFunctionalBlock
│   │   └── VRage.Game.ModAPI.IMyTextPanel
│   └── VRage.Game.ModAPI.IMySlimBlock
└── VRage.Game.ModAPI.IMyCubeGrid
```

**Features:**
- Shows complete interface inheritance tree
- Roots start with interfaces that extend no other interfaces
- Uses box-drawing characters
- Sorted alphabetically at each level
- Fully-qualified type names

**Note:** Interface implementations are NOT shown in tree files. Use hierarchy search commands instead.

## Indexer Implementation (`index_code.py`)

### Data Structures

The indexer uses these dataclasses:

```python
@dataclass
class IndexEntry:
    namespace: str
    declaring_type: str
    method: str
    symbol_name: str
    entry_type: str  # 'declaration' or 'usage'
    file_path: str
    start_line: int
    end_line: int
    description: str
    access: str = ""       # public, private, protected, internal
    modifiers: str = ""    # static, virtual, override, abstract, readonly, etc.
    member_type: str = ""  # return type (methods) or field/property/event type
    params: str = ""       # parameter list with parens (methods/constructors only)

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

@dataclass
class ClassHierarchyEntry:
    child_namespace: str
    child_class: str
    parent_namespace: str
    parent_class: str
    file_path: str
    start_line: int
    end_line: int

@dataclass
class InterfaceHierarchyEntry:
    child_namespace: str
    child_interface: str
    parent_namespace: str
    parent_interface: str
    file_path: str
    start_line: int
    end_line: int

@dataclass
class InterfaceImplementationEntry:
    implementing_namespace: str
    implementing_type: str
    interfaces: str  # Comma-separated
    file_path: str
    start_line: int
    end_line: int
```

### Two-Pass Processing

**Pass 1:** Collect all declarations
- Builds sets of declared types for each category
- Extracts hierarchy relationships from base lists
- No usage detection yet

**Pass 2:** Collect usages
- Uses shared declaration sets from Pass 1
- Identifies identifier usages by checking against known declarations
- Skips declaration contexts

### Hierarchy Extraction Logic

**In `_process_class()` and `_process_struct()`:**
1. Look for `base_list` child node
2. Extract all type names from base list
3. Check first item against `declared_interfaces` (from pass 1)
4. If first item is not an interface → it's a base class (classes only)
5. Create `ClassHierarchyEntry` for base class relationship
6. Remaining items (or all if first was interface) are interfaces
7. Collect interfaces into `InterfaceImplementationEntry`

**In `_process_interface()`:**
1. Look for `base_list` child node
2. All items in the list are parent interfaces
3. Create `InterfaceHierarchyEntry` for each parent

### Type Resolution

- Uses `declared_interfaces` and `declared_classes` sets from pass 1
- Checks if type name exists in `declared_interfaces` to identify it
- Uses namespace context to resolve unqualified names
- Falls back to naming convention (I-prefix) as heuristic if needed

### Generic Type Handling

- Strips generic parameters: `List<T>` becomes `List`
- Stores only the base type name in hierarchy entries

### Tree Generation

After building CSV files:

1. **Build in-memory graph structures:**
   - For classes: map of `parent_class` → list of `child_class`
   - For interfaces: map of `parent_interface` → list of `child_interface`

2. **Find root nodes:**
   - Classes: those that don't appear as children (or have `System.Object` as parent)
   - Interfaces: those that don't appear as children

3. **Traverse recursively:**
   - Start from each root
   - Use depth-first traversal
   - Track visited nodes to avoid cycles

4. **Format with box-drawing characters:**
   - `├──` for non-last children
   - `└──` for last child
   - `│   ` for continuation lines
   - `    ` for spacing after last child

5. **Write to text files:**
   - `class_hierarchy.txt`
   - `interface_hierarchy.txt`
   - Sort children alphabetically at each level

## Search Tool Implementation (`search_code.py`)

### Argument Parsing

Detects hierarchy subcommands:

```python
HIERARCHY_SUBCOMMANDS = {"parent", "children", "implements", "implementors"}

if args.symbol_type in HIERARCHY_SUBCOMMANDS:
    # Handle hierarchy query
else:
    # Handle declaration/usage query
```

### File Mapping

```python
CATEGORY_FILES = {
    "class": ("class_declarations.csv", "class_usages.csv"),
    "method": ("method_declarations.csv", "method_usages.csv"),
    "enum": ("enum_declarations.csv", "enum_usages.csv"),
    "struct": ("struct_declarations.csv", "struct_usages.csv"),
    "interface": ("interface_declarations.csv", "interface_usages.csv"),
    "field": ("field_declarations.csv", "field_usages.csv"),
    "property": ("property_declarations.csv", "property_usages.csv"),
    "event": ("event_declarations.csv", "event_usages.csv"),
    "constructor": ("constructor_declarations.csv", "constructor_usages.csv"),
    "namespace": ("namespace_declarations.csv", "namespace_usages.csv"),
}
```

### Hierarchy Query Logic

**For `parent` and `implements`:**
1. Search child/implementing column
2. Output one line per match with simple format

**For `children` and `implementors`:**
1. Search parent/interface column
2. Group all matches by parent/interface
3. Aggregate children/implementors into compressed format
4. Output one line per group

### Namespace Compression

The `compress_namespace_hierarchy()` function:
- Parses FQNs into namespace paths + type names
- Builds tree structure grouping by shared prefixes
- Flattens single-child chains: `A.B.C.Class`
- Groups multiple children: `A.B.(Class1,Class2)`
- Nested grouping: `A.(B.(C1,C2),D.E)`

### Output Formatting

```python
# One-to-one (parent, implements)
print(f"{child_namespace}.{child_name}:{parent_namespace}.{parent_name}")

# One-to-many (children, implementors)
compressed = compress_namespace_hierarchy(children)
print(f"{parent_namespace}.{parent_name}|{compressed}")
```

## Backward Compatibility

Standard search commands remain unchanged:
```bash
uv run search_code.py class declaration MyGrid
uv run search_code.py method usage GetPosition
```

Hierarchy subcommands are additions that don't affect existing functionality.
