# Space Engineers Game Code Skill

This skill provides access to decompiled C# source code from Space Engineers version 1, enabling code search and analysis for mod, plugin, and script development.

## Overview

Skill maintains the following data under the `Data` junction (which points
to `%USERPROFILE%\.se-dev\game-code\`):

- **Data/Decompiled/** - Full decompiled C# source organized by assembly
- **Data/Content/** - Game content files (definitions, translations, blueprints)
- **Data/CodeIndex/** - Pre-built CSV indexes for fast symbol lookup
- **Data/.git/** - Local Git repository tracking every decompilation; commit
  message is the game version label (e.g. `1.208.015 b4`)
- **Data/game_version.txt** - Recorded version constants; used to detect game updates

## Setup

Run preparation steps in `Prepare.md` if `Prepare.DONE` is missing. Requires:

- Python 3.11+
- Command line `git` client on `PATH`
- .NET SDK (for `ilspycmd`)

Preparation will:
1. Create `Data` junction and local Git repository inside it (with
   initial commit of `.gitignore`)
2. Detect current game version by inspecting binaries
3. Wipe `Decompiled/`, `Content/` and `CodeIndex/` if version differs from
   recorded one
4. Decompile game assemblies and commit them with version label
5. Copy game content
6. Build code index

## Code Index

### Index Files

Located in `Data/CodeIndex/` after preparation:

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
| `namespace` | Namespace containing the symbol |
| `declaring_type` | Class/struct/interface containing the symbol |
| `method` | Method containing the symbol (empty for type-level items) |
| `symbol_name` | Field/property/event name (for member indices) |
| `type` | Either `declaration` or `usage` |
| `file_path` | Relative path from `Data/Decompiled/` folder |
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
| `namespace` | Full namespace of declaring class |
| `declaring_type` | Class name (for inner classes: `ParentClass.ChildClass`) |
| `method_name` | Method name |
| `signature` | Full method signature on single line (whitespace normalized) |
| `file_path` | Relative path from `Data/Decompiled/` folder |
| `start_line` | Starting line of signature |
| `end_line` | Ending line of signature (not whole method body) |
| `description` | XML doc comment before the method |

Signature index includes all method types: abstract methods (no body), inline `=>` methods, and block `{...}` methods. Property getters/setters are NOT indexed as signatures; they appear in field index.

### Indexer: index_code.py

Builds code index using Tree-sitter for C# parsing. Uses parallel processing with two passes:

1. **Pass 1** - Collect all declarations (namespaces, types, methods, variables)
2. **Pass 2** - Collect all usages by matching identifiers against known declarations

Usage:
```
uv run index_code.py <source_root_path> <output_directory>
```

## Code Search

### search_game_code.py

Search code index for symbols by category and type.

```
uv run search_game_code.py [options] <category> <symbol_type> <patterns...>
```

#### Positional Arguments

| Argument | Values | Description |
|----------|--------|-------------|
| `category` | `class`, `method`, `enum`, `struct`, `interface`, `field`, `property`, `event`, `constructor`, `namespace` | Symbol category to search |
| `symbol_type` | `declaration`, `usage`, `signature` (method only), `parent`, `children`, `implements`, `implementors` (hierarchy) | What to search for |
| `patterns` | One or more patterns | Search expressions (see below) |

**Note:** `method signature` is a special subcommand showing full method signatures with parameters. Hierarchy subcommands (`parent`, `children`, `implements`, `implementors`) work with `class` and `interface` categories.

#### Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message |
| `-c`, `--count` | Print only count of matches |
| `-l N`, `--limit N` | Limit output to N results |
| `-o N`, `--offset N` | Skip first N results (pagination) |
| `-n NS`, `--namespace NS` | Filter to namespace and its sub-namespaces |

#### Pattern Syntax

Patterns match against symbol name (not namespace):

| Prefix | Behavior |
|--------|----------|
| `text:X` or just `X` | Case-sensitive substring match (use `-i` for case-insensitive) |
| `re:X` | Case-sensitive regex, Python regex syntax (use `-i` for case-insensitive) |

Multiple patterns must all match (AND logic).

#### Output

- If no matches: prints `NO-MATCHES`
- Otherwise: prints `file_path:line` or `file_path:start-end` for each match (line ranges are inclusive)
- Results sorted by code depth (namespace.class.method nesting), then alphabetically

**Method signature output:** For `method signature` searches, output includes full signature text after file location, separated by pipe character:
```
file_path:start-end|signature_text
```

Example:
```
Sandbox.Game\Sandbox\Game\MyClass.cs:100-102|[Attribute] public static void MyMethod(int param)
```

Signature includes any attributes on preceding lines, normalized to single line with whitespace collapsed. Doc comments not included in signature text.

### Examples

Find class declarations containing "Toolbar":
```
uv run search_game_code.py class declaration Toolbar
```

Find all usages of methods matching "Get.*Position" regex:
```
uv run search_game_code.py method usage "re:Get.*Position"
```

Find enum declarations in Sandbox.Game namespace:
```
uv run search_game_code.py -n Sandbox.Game enum declaration ""
```

Count struct usages containing "Vector":
```
uv run search_game_code.py -c struct usage Vector
```

Paginate through interface declarations (first 20, then next 20):
```
uv run search_game_code.py -l 20 interface declaration ""
uv run search_game_code.py -l 20 -o 20 interface declaration ""
```

Find variable declarations with "Entity" in name within VRage namespace:
```
uv run search_game_code.py -n VRage field declaration Entity
```

Find method signatures containing "GetPosition":
```
uv run search_game_code.py method signature GetPosition
```

## Direct grep Search

For simple lookups, direct grep can be faster:

```
busybox.exe grep ",MyToolbar," Data/CodeIndex/class_declarations.csv
busybox.exe grep ",GetPosition," Data/CodeIndex/method_usages.csv
```

## Reading Source Files

After finding a symbol location, read source from `Data/Decompiled/`:

```
# Search result: VRage.Math/VRageMath/Vector3D.cs:13-245
# Read: Data/Decompiled/VRage.Math/VRageMath/Vector3D.cs
```

First folder in the path indicates the assembly (DLL) containing the code.

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
busybox.exe grep "pattern" Data/CodeIndex/class_declarations.csv
```

Use `uv run` to execute Python scripts with virtual environment.
