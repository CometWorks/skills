# Code Search Guide

Search the decompiled Space Engineers C# codebase efficiently.

**IMPORTANT:** All commands run on Windows. This skill folder must be the current working directory.

## Running Commands

Always change to this skill folder first:

```bash
cd skills/se-dev-server-code
uv run search_code.py class declaration MyToolbar
```

## Search Categories

| Category | What It Searches |
|----------|-----------------|
| `class` | Class declarations and usages |
| `interface` | Interface declarations and usages |
| `struct` | Struct declarations and usages |
| `enum` | Enum declarations and usages |
| `method` | Method declarations and usages |
| `field` | Field declarations and usages |
| `property` | Property declarations and usages |
| `event` | Event declarations and usages |
| `constructor` | Constructor declarations and usages |
| `namespace` | Namespace declarations and usages |

## Basic Usage

```bash
uv run search_code.py <category> <declaration|usage> <pattern>
```

### Find Declarations

```bash
uv run search_code.py class declaration MyToolbar
uv run search_code.py struct declaration Vector3D
uv run search_code.py interface declaration IMyTerminalBlock
uv run search_code.py enum declaration MyRelationsBetweenPlayerAndBlock
uv run search_code.py method declaration GetPosition
uv run search_code.py field declaration AngularDamping
uv run search_code.py property declaration IsWorking
uv run search_code.py event declaration IsWorkingChanged
uv run search_code.py constructor declaration MyCubeBlock
```

### Find Usages

```bash
uv run search_code.py -l 10 class usage MyToolbar
uv run search_code.py -l 10 method usage GetPosition
uv run search_code.py -l 10 struct usage Vector3D
```

### Search Method Signatures

Method signatures show the complete method declaration including modifiers, return type, parameters, and attributes:

```bash
# Find signatures by method name
uv run search_code.py method signature GetPosition

# Regex for exact match
uv run search_code.py method signature "re:^Build$"

# Limit results
uv run search_code.py -l 10 method signature GetPosition

# Filter by namespace
uv run search_code.py -n VRageMath method signature Normalize
```

**Output Format:** Signature searches show the full method signature after a pipe separator:
```
Sandbox.Game/MyClass.cs:100-102|public static void MyMethod(int param)
```

**Note:** Signatures are always declarations. There is no `method signature usage` - use `method usage` instead to find method call sites.

## Search Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help |
| `-c`, `--count` | Print only match count |
| `-l N`, `--limit N` | Limit to N results |
| `-o N`, `--offset N` | Skip first N results |
| `-n NS`, `--namespace NS` | Filter by namespace prefix |

### Count Before Fetching

```bash
uv run search_code.py -c class usage MyEntity
# Output: 1247

uv run search_code.py -l 20 class usage MyEntity
```

### Paginate Large Results

```bash
uv run search_code.py -l 20 class usage MyEntity
uv run search_code.py -l 20 -o 20 class usage MyEntity
uv run search_code.py -l 20 -o 40 class usage MyEntity
```

### Filter by Namespace

```bash
uv run search_code.py -n Sandbox.Game class declaration ""
uv run search_code.py -n VRageMath method declaration Add
```

## Pattern Syntax

Patterns match against the symbol name (not namespace):

| Prefix | Behavior |
|--------|----------|
| `text:X` or just `X` | Case-sensitive substring match (use `-i` for case-insensitive) |
| `re:X` | Case-sensitive regex, Python regex syntax (use `-i` for case-insensitive) |

Multiple patterns use AND logic (all must match).

### Examples

```bash
# Substring match (default)
uv run search_code.py class declaration Toolbar

# Explicit text match
uv run search_code.py class declaration "text:Toolbar"

# Regex for exact match
uv run search_code.py class declaration "re:^MyToolbar$"

# Regex patterns
uv run search_code.py class declaration "re:^My.*Block$"
uv run search_code.py method declaration "re:^Get.*Position$"
uv run search_code.py struct declaration "re:^Vector[23]D$"
```

### Multiple Patterns

```bash
uv run search_code.py method declaration Get Position
```

Both "Get" AND "Position" must appear in the name.

## Reading Output

### No Matches
```
NO-MATCHES
```

### Standard Output
```
relative_path:line
relative_path:start-end
```

Lines are inclusive (both start and end are part of the match).

Results are sorted by code depth, then alphabetically.

### Reading Source Files

The `relative_path` is relative to the `Decompiled/` folder:

```bash
# Search result: VRage.Math/VRageMath/Vector3D.cs:13-2293
# Read file: Decompiled/VRage.Math/VRageMath/Vector3D.cs
```

The first folder indicates the assembly (DLL). From the second level, folders match namespace hierarchy.

## Assembly Reference

| Assembly | Contains |
|----------|----------|
| `SpaceEngineersDedicated` | Server entry point, startup, and configuration |
| `VRage.Dedicated` | Dedicated server framework and lifecycle |
| `VRage.RemoteClient.Core` | Remote client/RCON support |
| `VRage.Math` | Math types: Vector3, Matrix, BoundingBox, etc. |
| `VRage.Game` | Game definitions, object builders |
| `VRage.Library` | Core utilities |
| `Sandbox.Game` | Game logic, entities, blocks |
| `Sandbox.Common` | Shared game code |
| `SpaceEngineers.Game` | SE-specific game code |
| `SpaceEngineers.ObjectBuilders` | Save data structures |

## Best Practices

1. **Start with declarations** - Find definitions before usages
2. **Use regex for exact names** - `"re:^Vector3D$"` avoids Vector3DI, Vector3D_Extensions, etc.
3. **Check the assembly** - First folder in path shows which DLL
4. **Count first** - Use `-c` to see match count before fetching all
5. **Paginate large results** - Use `-l` and `-o` for incremental browsing
6. **Query at most 10-20 results** - Keep context manageable

## Next Steps

- **Hierarchy searches**: See `HierarchySearch.md` for class/interface relationships
- **Advanced patterns**: See `Advanced.md` for complex regex and workflows
- **Technical details**: See `Implementation.md` for CSV structures and internals
