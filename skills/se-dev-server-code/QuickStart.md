# Code Search Quick Start

This skill provides instant access to Space Engineers' decompiled C# source code through indexed search.

## Prerequisites

If `Prepare.DONE` is missing, run the preparation first (see `Prepare.md`).

## Essential Commands

All commands run from this skill folder:

```bash
cd skills/se-dev-server-code
```

### Find a Class Definition

```bash
uv run search_code.py class declaration MyToolbar
```

Output: `Sandbox.Game/Sandbox/Game/Gui/MyToolbar.cs:42-1250`

### Find Where a Class is Used

```bash
uv run search_code.py -l 10 class usage MyToolbar
```

Shows first 10 usage locations.

### Find a Method Definition

```bash
uv run search_code.py method declaration GetPosition
```

### Find Method Signatures

```bash
uv run search_code.py method signature GetPosition
```

Shows full method signatures including parameters and return types. See `CodeSearch.md` for more details.

### Find Class Hierarchy

```bash
uv run search_code.py class parent MyGrid
```

Output: `Sandbox.Game.MyGrid:VRage.Game.Entity.MyEntity`

## Reading Results

Results show: `relative_path:line` or `relative_path:start-end`

To read the actual code:
- Results are relative to the `Decompiled/` folder
- Example: `VRage.Math/VRageMath/Vector3D.cs:13-2293`
- Read: `Decompiled/VRage.Math/VRageMath/Vector3D.cs`

## Next Steps

- **Full search guide**: See `CodeSearch.md` for all search options
- **Hierarchy queries**: See `HierarchySearch.md` for class/interface relationships
- **Advanced techniques**: See `Advanced.md` for regex, pagination, and more
