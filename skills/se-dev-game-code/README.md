# Space Engineers Game Code Skill

This skill provides access to decompiled C# source code from Space Engineers version 1, enabling code search and analysis for mod, plugin, and script development.

## Overview

The skill maintains:
- **Decompiled/** - Full decompiled C# source organized by assembly
- **Content/** - Game content files (definitions, translations, blueprints)
- **CodeIndex/** - Pre-built CSV indexes for fast symbol lookup

## Setup

Run the preparation steps in `Prepare.md` if `Prepare.DONE` is missing. This will:
1. Decompile the game assemblies
2. Copy game content
3. Build the code index

## Code Index

### Index Files

Located in `CodeIndex/` after preparation:

| File | Contains |
|------|----------|
| `namespace_declarations.csv` | Namespace declarations |
| `namespace_usages.csv` | Namespace usages |
| `interface_declarations.csv` | Interface declarations |
| `interface_usages.csv` | Interface usages |
| `class_declarations.csv` | Class declarations |
| `class_usages.csv` | Class usages |
| `struct_declarations.csv` | Struct declarations |
| `struct_usages.csv` | Struct usages |
| `enum_declarations.csv` | Enum declarations |
| `enum_usages.csv` | Enum usages |
| `method_declarations.csv` | Method declarations |
| `method_usages.csv` | Method usages |
| `method_signatures.csv` | Method signatures (different columns, see below) |
| `field_declarations.csv` | Field declarations |
| `field_usages.csv` | Field usages |
| `property_declarations.csv` | Property declarations |
| `property_usages.csv` | Property usages |
| `event_declarations.csv` | Event declarations |
| `event_usages.csv` | Event usages |
| `constructor_declarations.csv` | Constructor declarations |
| `constructor_usages.csv` | Constructor usages |

### CSV Structure

Most index files share this column structure:

```
namespace,declaring_type,method,symbol_name,type,file_path,start_line,end_line,description,access,modifiers,member_type,params
```

| Column | Description |
|--------|-------------|
| `namespace` | The namespace containing the symbol |
| `declaring_type` | The class/struct/interface containing the symbol |
| `method` | The method containing the symbol (empty for type-level items) |
| `symbol_name` | Field/property/event name (for member indices) |
| `type` | Either `declaration` or `usage` |
| `file_path` | Relative path from `Decompiled/` folder |
| `start_line` | Starting line number |
| `end_line` | Ending line number |
| `description` | XML doc comment (for declarations only) |
| `access` | Access modifier: `public`, `private`, `protected`, `internal`, etc. (member declarations only) |
| `modifiers` | Other modifiers: `static`, `virtual`, `override`, `abstract`, `readonly`, etc. (member declarations only) |
| `member_type` | Return type (methods), field/property/event type (member declarations only) |
| `params` | Parameter list including parentheses, e.g. `(int x, string name)` (methods/constructors only) |

### Method Signatures CSV Structure

**Note:** The `method_signatures.csv` file has a **different column structure**:

```
namespace,declaring_type,method_name,signature,file_path,start_line,end_line,description
```

| Column | Description |
|--------|-------------|
| `namespace` | Full namespace of the declaring class |
| `declaring_type` | Class name (for inner classes: `ParentClass.ChildClass`) |
| `method_name` | The method name |
| `signature` | Full method signature on a single line (whitespace normalized) |
| `file_path` | Relative path from `Decompiled/` folder |
| `start_line` | Starting line of the signature |
| `end_line` | Ending line of the signature (not the whole method body) |
| `description` | XML doc comment before the method |

The signature index includes all method types: abstract methods (no body), inline `=>` methods, and block `{...}` methods. Property getters/setters are NOT indexed as signatures; they appear in the field index.

### Indexer: index_code.py

Builds the code index using Tree-sitter for C# parsing. Uses parallel processing with two passes:

1. **Pass 1** - Collect all declarations (namespaces, types, methods, variables)
2. **Pass 2** - Collect all usages by matching identifiers against known declarations

Usage:
```
uv run index_code.py <source_root_path> <output_directory>
```

## Code Search

### search_code.py

Search the code index for symbols by category and type.

```
uv run search_code.py [options] <category> <symbol_type> <patterns...>
```

#### Positional Arguments

| Argument | Values | Description |
|----------|--------|-------------|
| `category` | `class`, `method`, `enum`, `struct`, `interface`, `field`, `property`, `event`, `constructor`, `namespace` | Symbol category to search |
| `symbol_type` | `declaration`, `usage`, `signature` (method only), `parent`, `children`, `implements`, `implementors` (hierarchy) | What to search for |
| `patterns` | One or more patterns | Search expressions (see below) |

**Note:** `method signature` is a special subcommand that shows full method signatures with parameters. Hierarchy subcommands (`parent`, `children`, `implements`, `implementors`) work with `class` and `interface` categories.

#### Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message |
| `-c`, `--count` | Print only the count of matches |
| `-l N`, `--limit N` | Limit output to N results |
| `-o N`, `--offset N` | Skip first N results (pagination) |
| `-n NS`, `--namespace NS` | Filter to namespace and its sub-namespaces |

#### Pattern Syntax

Patterns match against the symbol name (not the namespace):

| Prefix | Behavior |
|--------|----------|
| `text:X` or just `X` | Case-sensitive substring match (use `-i` for case-insensitive) |
| `re:X` | Case-sensitive regex, Python regex syntax (use `-i` for case-insensitive) |

Multiple patterns must all match (AND logic).

#### Output

- If no matches: prints `NO-MATCHES`
- Otherwise: prints `file_path:line` or `file_path:start-end` for each match (line ranges are inclusive)
- Results sorted by code depth (namespace.class.method nesting), then alphabetically

**Method signature output:** For `method signature` searches, the output includes the full signature text after the file location, separated by a pipe character:
```
file_path:start-end|signature_text
```

Example:
```
Sandbox.Game\Sandbox\Game\MyClass.cs:100-102|[Attribute] public static void MyMethod(int param)
```

The signature includes any attributes on preceding lines, normalized to a single line with whitespace collapsed. Doc comments are not included in the signature text.

### Examples

Find class declarations containing "Toolbar":
```
uv run search_code.py class declaration Toolbar
```

Find all usages of methods matching "Get.*Position" regex:
```
uv run search_code.py method usage "re:Get.*Position"
```

Find enum declarations in Sandbox.Game namespace:
```
uv run search_code.py -n Sandbox.Game enum declaration ""
```

Count struct usages containing "Vector":
```
uv run search_code.py -c struct usage Vector
```

Paginate through interface declarations (first 20, then next 20):
```
uv run search_code.py -l 20 interface declaration ""
uv run search_code.py -l 20 -o 20 interface declaration ""
```

Find variable declarations with "Entity" in name within VRage namespace:
```
uv run search_code.py -n VRage field declaration Entity
```

Find method signatures containing "GetPosition":
```
uv run search_code.py method signature GetPosition
```

## Direct grep Search

For simple lookups, direct grep can be faster:

```
busybox.exe grep ",MyToolbar," CodeIndex/class_declarations.csv
busybox.exe grep ",GetPosition," CodeIndex/method_usages.csv
```

## Reading Source Files

After finding a symbol location, read the source from `Decompiled/`:

```
# Search result: VRage.Math/VRageMath/Vector3D.cs:13-245
# Read: Decompiled/VRage.Math/VRageMath/Vector3D.cs
```

The first folder in the path indicates the assembly (DLL) containing the code.

## Common Assemblies

| Assembly | Contains |
|----------|----------|
| `VRage.Math` | Math types (Vector3, Matrix, BoundingBox) |
| `VRage.Game` | Game definitions, object builders |
| `VRage.Library` | Core utilities |
| `Sandbox.Game` | Game logic, entities, blocks |
| `Sandbox.Common` | Shared game code |
| `SpaceEngineers.Game` | SE-specific game code |
| `SpaceEngineers.ObjectBuilders` | Save data structures |

## Windows Command Line

All commands run on Windows. Use `busybox.exe` for UNIX-like commands with forward slashes in paths:

```
busybox.exe grep "pattern" CodeIndex/class_declarations.csv
```

Use `uv run` to execute Python scripts with the virtual environment.
