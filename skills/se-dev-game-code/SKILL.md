---
name: se-dev-game-code
description: Allows reading the decompiled C# code of Space Engineers version 1
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*Clean.bat*), Bash(*run_prepare.sh*), Bash(*test_search.bat*), Bash(*uv run search_code.py *), Bash(*uv run index_code.py *), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Game Code Skill

Allows reading the decompiled C# code of Space Engineers version 1.

**⚠️ CRITICAL: Commands run in a UNIX shell (busybox), NOT Windows CMD. Use bash syntax!**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - This will NOT work

**Actions:**

- **prepare**: Run the one-time preparation (Prepare.bat)
- **bash**: Run UNIX shell commands via busybox
- **search**: Run code searches using `search_code.py`
- **test**: Test this skill by running `test_search.bat`

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-game-code` | Show this help |
| 2 | Prepare keywords | `se-dev-game-code prepare`, `se-dev-game-code setup`, `se-dev-game-code init` | prepare |
| 3 | Bash/shell keywords | `se-dev-game-code bash`, `se-dev-game-code grep`, `se-dev-game-code cat` | bash |
| 4 | Search keywords | `se-dev-game-code search`, `se-dev-game-code find class`, `se-dev-game-code lookup` | search |
| 5 | Test keywords | `se-dev-game-code test`, `se-dev-game-code verify`, `se-dev-game-code check` | test |

## Getting Started

**⚠️ CRITICAL: Before running ANY commands, read [CommandExecution.md](CommandExecution.md) to avoid common mistakes that cause command failures.**

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps first. See the [prepare action](./actions/prepare.md).

During preparation the current game version is stored into `CodeIndex/game_version.txt`.

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - How to run commands correctly on Windows

## Code Search Documentation

- **[QuickStart.md](QuickStart.md)** - More examples and quick reference
- **[CodeSearch.md](CodeSearch.md)** - Complete guide to searching classes, methods, fields, etc.
- **[HierarchySearch.md](HierarchySearch.md)** - Finding class/interface inheritance and implementations
- **[Advanced.md](Advanced.md)** - Power user techniques for complex searches
- **[Troubleshooting.md](Troubleshooting.md)** - What to do when searches return NO-MATCHES or too many results
- **[Implementation.md](Implementation.md)** - Technical details for skill contributors (optional)

## Quick Search Examples

```bash
# Find class declarations
uv run search_code.py class declaration MyCubeBlock

# Find method signatures
uv run search_code.py method signature UpdateBeforeSimulation

# Find class hierarchy
uv run search_code.py class children MyTerminalBlock

# Count results before viewing (useful for large result sets)
uv run search_code.py class usage MyEntity --count

# Limit number of results
uv run search_code.py class usage MyEntity --limit 10

# Paginate through results
uv run search_code.py class usage MyEntity --limit 10 --offset 0
uv run search_code.py class usage MyEntity --limit 10 --offset 20
```

Always check the game code when:
- You're unsure about the game's internal APIs and how to interface with them.
- The inner workings of Space Engineers is unclear.

## Custom Scripting

For building your own utility scripts to work with the indexes and decompiled code:

- **[ScriptingGuide.md](ScriptingGuide.md)** - How to write Python scripts, use BusyBox, handle Windows paths

## Game Content Data

The textual part of the game's `Content` is copied into the `Content` folder for free text search:
- Language translations, including the string IDs
- Block and other entity definitions
- Default blueprints and scenarios
- See [ContentTypes.md](ContentTypes.md) for the full list of content types

## General Rules

- In the `Decompiled` folder search only inside the C# source files (*.cs) in general. If you work on transpiler or preloader patches, then also search in the IL code (*.il) files.
- In the `Content` folder search the files appropriate for the task. See [ContentTypes.md](ContentTypes.md) for the list of types.
- Do not search for decompiled game code outside the `Decompiled` folder which is at the same level as this skill file. The decompiled game source tree must be there if the preparation succeeded.
- Do not search for game content data outside the `Content` folder which is at the same level as this skill file. The copied game content must be there if the preparation succeeded.

## Action References

Follow the detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
- [search action](./actions/search.md) - Running code searches
- [test action](./actions/test.md) - Testing this skill

## Remarks

The original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
