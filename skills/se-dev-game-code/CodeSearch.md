# Code Search Guide

**IMPORTANT:** All commands run on Windows. This skill folder must be the current working directory.

## Running Commands

Always change to this skill folder first, then run commands:

```
cd skills/se-dev-game-code
uv run search_code.py class declaration MyToolbar
```

## Index Files

Located in `CodeIndex/` folder after preparation:

| Index File | Contains | Use For |
|------------|----------|---------|
| `namespace_declarations.csv` | Namespace declarations | Finding which assembly defines a namespace |
| `interface_declarations.csv` | Interface declarations | Finding interface definitions |
| `interface_usages.csv` | Interface usages | Finding interface implementations and references |
| `class_declarations.csv` | Class declarations | Finding class definitions |
| `class_usages.csv` | Class usages | Finding class references |
| `struct_declarations.csv` | Struct declarations | Finding struct definitions |
| `struct_usages.csv` | Struct usages | Finding struct references |
| `enum_declarations.csv` | Enum declarations | Finding enum definitions |
| `enum_usages.csv` | Enum usages | Finding enum references |
| `method_declarations.csv` | Method declarations | Finding method signatures |
| `method_usages.csv` | Method usages | Finding method call sites |
| `variable_declarations.csv` | Fields, properties | Finding variable definitions |
| `variable_usages.csv` | Variable usages | Finding variable references |

## CSV Column Structure

All index files share this structure:

```
namespace,declaring_type,method,variable_name,type,file_path,start_line,end_line,description
```

- `namespace` - The namespace containing the symbol
- `declaring_type` - The class/struct/interface containing the symbol
- `method` - The method containing the symbol (empty for type-level declarations)
- `variable_name` - Variable/field/property name (for variables.csv)
- `type` - Either `declaration` or `usage`
- `file_path` - Relative path from `Decompiled/` folder
- `start_line`, `end_line` - Line range in source file
- `description` - XML doc comment summary (for declarations)

## Using search_code.py

The primary search tool. Run from this skill folder:

```
uv run search_code.py [options] <category> <symbol_type> <patterns...>
```

### Arguments

| Argument | Values | Description |
|----------|--------|-------------|
| `category` | `class`, `method`, `enum`, `struct`, `interface`, `variable` | Symbol category |
| `symbol_type` | `declaration`, `usage` | Find definitions or references |
| `patterns` | One or more | Search patterns (see below) |

### Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help |
| `-c`, `--count` | Print only match count |
| `-l N`, `--limit N` | Limit to N results |
| `-o N`, `--offset N` | Skip first N results |
| `-n NS`, `--namespace NS` | Filter by namespace prefix |

### Pattern Syntax

Patterns match against the symbol name (not namespace):

| Prefix | Behavior |
|--------|----------|
| `text:X` or just `X` | Case-insensitive substring match |
| `re:X` | Case-insensitive regex match (Python regex syntax) |

Multiple patterns use AND logic (all must match).

### Output Format

- No matches: `NO-MATCHES`
- Matches (one line match): `relative_source_file_path:line` or `relative_source_file_path:start_line-end_line`
- Results sorted by code depth, then alphabetically inside the same depth

The `relative_source_file_path` is relative to the `Decompiled` folder which is next to this document.

In count mode (`--count` or `-c`) only the number of search hits are printed instead of the actual matches.

If you expect too many hits, then first count, then paginate as needed. Try not to query more than 10 results at a time.

## Examples

### Find Declarations

```
uv run search_code.py class declaration MyToolbar
uv run search_code.py struct declaration Vector3D
uv run search_code.py interface declaration IMyTerminalBlock
uv run search_code.py enum declaration MyRelationsBetweenPlayerAndBlock
uv run search_code.py method declaration GetPosition
uv run search_code.py variable declaration AngularDamping
```

### Find Usages

```
uv run search_code.py -l 10 class usage MyToolbar
uv run search_code.py -l 10 method usage GetPosition
uv run search_code.py -l 10 struct usage Vector3D
```

### Regex Patterns

```
uv run search_code.py class declaration "re:^My.*Block$"
uv run search_code.py method declaration "re:^Get.*Position$"
uv run search_code.py struct declaration "re:^Vector[23]D$"
```

### Namespace Filtering

```
uv run search_code.py -n Sandbox.Game class declaration ""
uv run search_code.py -n VRageMath method declaration Add
uv run search_code.py -n Sandbox.Engine.Physics -l 5 class declaration ""
```

### Pagination

```
uv run search_code.py -l 20 class usage MyEntity
uv run search_code.py -l 20 -o 20 class usage MyEntity
uv run search_code.py -l 20 -o 40 class usage MyEntity
```

### Count Mode

```
uv run search_code.py -c class usage MyEntity
uv run search_code.py -c struct usage Vector3D
```

### Multiple Patterns

```
uv run search_code.py method declaration Get Position
```

## Reading Source Files

After finding their relative paths, read the actual source files under `Decompiled/`. 

For example:
```
# Search result: VRage.Math/VRageMath/Vector3D.cs:13-2293
# Read: Decompiled/VRage.Math/VRageMath/Vector3D.cs
```

The first folder in the relative path indicates the assembly (DLL), from the second level the folders match the namespace hierarchy.

## Tips

1. **Start with declarations** - Find definitions before usages
2. **Use regex for exact names** - `"re:^Vector3D$"` avoids matching Vector3DI, Vector3D_Extensions, etc.
3. **Check the assembly** - The first folder in `file_path` shows which DLL contains the code
4. **Use count first** - Check `-c` to see how many matches before fetching all
5. **Paginate large results** - Use `-l` and `-o` to browse incrementally

## Assembly Reference

| Assembly | Contains |
|----------|----------|
| `VRage.Math` | Math types: Vector3, Matrix, BoundingBox, etc. |
| `VRage.Game` | Game definitions, object builders |
| `VRage.Library` | Core utilities |
| `Sandbox.Game` | Game logic, entities, blocks |
| `Sandbox.Common` | Shared game code |
| `SpaceEngineers.Game` | SE-specific game code |
| `SpaceEngineers.ObjectBuilders` | Save data structures |
