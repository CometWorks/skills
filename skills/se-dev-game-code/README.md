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
| `namespaces.csv` | Namespace declarations |
| `interfaces.csv` | Interface declarations and usages |
| `classes.csv` | Class declarations and usages |
| `structs.csv` | Struct declarations and usages |
| `enums.csv` | Enum declarations and usages |
| `methods.csv` | Method declarations and usages |
| `variables.csv` | Fields, properties, and variable usages |

### CSV Structure

All index files share this column structure:

```
namespace,declaring_type,method,variable_name,type,file_path,start_line,end_line,description
```

| Column | Description |
|--------|-------------|
| `namespace` | The namespace containing the symbol |
| `declaring_type` | The class/struct/interface containing the symbol |
| `method` | The method containing the symbol (empty for type-level items) |
| `variable_name` | Variable/field/property name (for variables.csv) |
| `type` | Either `declaration` or `usage` |
| `file_path` | Relative path from `Decompiled/` folder |
| `start_line` | Starting line number |
| `end_line` | Ending line number |
| `description` | XML doc comment (for declarations only) |

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
| `category` | `class`, `method`, `enum`, `struct`, `interface`, `variable` | Symbol category to search |
| `symbol_type` | `declaration`, `usage` | Whether to find definitions or references |
| `patterns` | One or more patterns | Search expressions (see below) |

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
| `text:X` or just `X` | Case-insensitive substring match |
| `re:X` | Case-insensitive regex match (Python regex syntax) |

Multiple patterns must all match (AND logic).

#### Output

- If no matches: prints `NO-MATCHES`
- Otherwise: prints `file_path:line` or `file_path:start-end` for each match
- Results sorted by code depth (namespace.class.method nesting), then alphabetically

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
uv run search_code.py -n VRage variable declaration Entity
```

## Direct grep Search

For simple lookups, direct grep can be faster:

```
busybox.exe grep ",MyToolbar," CodeIndex/classes.csv | busybox.exe grep ",declaration,"
busybox.exe grep ",GetPosition," CodeIndex/methods.csv | busybox.exe grep ",usage,"
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
busybox.exe grep "pattern" CodeIndex/classes.csv
```

Use `uv run` to execute Python scripts with the virtual environment.
