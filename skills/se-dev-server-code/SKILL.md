---
name: se-dev-server-code
description: Allows reading the decompiled C# code of the Space Engineers Dedicated Server
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*prepare.sh*), Bash(*Clean.bat*), Bash(*test_search_server_code.bat*), Bash(*uv run search_server_code.py *), Bash(*uv run index_code.py *), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Server Code Skill

Allows reading the decompiled C# code of the Space Engineers Dedicated Server. Server "game logic" is largely the same as game (client) runs. Entry point (main executable), some aspects of logging and configuration differ. Also, some libraries are not used by server, but they may still present to provide necessary data structures and some backend functionality.

**⚠️ CRITICAL: Commands run in a UNIX shell. Use bash syntax. On Windows this is BusyBox; on Linux use the native shell.**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - This will NOT work

**Actions:**

- **prepare**: Run the one-time preparation (`Prepare.bat` on Windows, `prepare.sh` on Linux)
- **bash**: Run UNIX shell commands via busybox
- **search**: Run code searches using `search_server_code.py`
- **test**: Test this skill by running `test_search_server_code.bat`

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-server-code` | Show this help |
| 2 | Prepare keywords | `se-dev-server-code prepare`, `se-dev-server-code setup`, `se-dev-server-code init` | prepare |
| 3 | Bash/shell keywords | `se-dev-server-code bash`, `se-dev-server-code grep`, `se-dev-server-code cat` | bash |
| 4 | Search keywords | `se-dev-server-code search`, `se-dev-server-code find class`, `se-dev-server-code lookup` | search |
| 5 | Test keywords | `se-dev-server-code test`, `se-dev-server-code verify`, `se-dev-server-code check` | test |

## Requirements

Host system must have the following on `PATH`:

- **Python** 3.11 or newer
- **git** command line client (used to version each decompiled server build)
- **dotnet** SDK (for installing `ilspycmd`)

## Getting Started

**⚠️ CRITICAL: Before running ANY commands, read [CommandExecution.md](CommandExecution.md) to avoid common mistakes that cause command failures.**

If `Prepare.DONE` file is missing in this folder, you MUST run one-time preparation steps first. See the [prepare action](./actions/prepare.md).

If server auto-detection fails, set `SE_SERVER_ROOT` before running preparation script. May point to either dedicated server root or directly to `DedicatedServer64` directory.

## Folder Layout

After preparation the skill folder contains a `Data` junction/symlink. Actual data lives outside the skill folder so it is preserved across `Clean.bat` / `Prepare.bat` / `prepare.sh` cycles.

```
skills/se-dev-server-code/
├── Data/                 (junction/symlink → per-user persistent server-code data)
│   ├── .git/             local Git repository tracking decompiled sources
│   ├── .gitignore        ignores CodeIndex/, Content/, __pycache__, *.py[cod], *.bak, *.log
│   ├── game_version.txt  recorded SE_VERSION / CLIENT_BUILD_NUMBER / SERVER_BUILD_NUMBER
│   ├── Decompiled/       decompiled C# sources, organised per assembly (committed)
│   ├── Content/          textual server content (NOT committed - regenerated)
│   └── CodeIndex/        CSV indexes (NOT committed - regenerated)
├── Bin64/                (junction/symlink → server's DedicatedServer64, removed after preparation)
└── ...                   skill scripts and documentation
```

The `Data` folder is a junction/symlink to per-user persistent server-code data directory (`%USERPROFILE%\.se-dev\server-code` on Windows, `~/.se-dev/server-code` on Linux). Treat `Data/Decompiled`, `Data/Content` and `Data/CodeIndex` exactly as before.

## Local Versioning of Decompiled Sources

The `Data` folder is a local Git repository. Every successful preparation creates a commit of the decompiled C# sources whose message is server version label, e.g. `1.208.015 b4`.

This means:

- **All previously decompiled server versions are preserved** in local Git history. You can `git checkout` any past commit inside `Data/` to inspect or diff against older build.
- **Server updates are detected automatically** by comparing binaries' embedded version constants with `Data/game_version.txt`. If they differ (or file is missing), `Decompiled/`, `Content/` and `CodeIndex/` are wiped and fresh decompilation runs.
- This makes it easy to **update plugins, mods and scripts for compatibility with new server releases**: diff the relevant source between two commits inside `Data/` to see exactly what changed.

Repository uses internal author/email (`se-dev-skills@localhost`) so commits work even on machines without configured global Git identity.

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - Windows command execution details; on Linux keep bash syntax and use `prepare.sh`

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
uv run search_server_code.py class declaration MyCubeBlock

# Find method signatures
uv run search_server_code.py method signature UpdateBeforeSimulation

# Find class hierarchy
uv run search_server_code.py class children MyTerminalBlock

# Count results before viewing (useful for large result sets)
uv run search_server_code.py class usage MyEntity --count

# Limit number of results
uv run search_server_code.py class usage MyEntity --limit 10

# Paginate through results
uv run search_server_code.py class usage MyEntity --limit 10 --offset 0
uv run search_server_code.py class usage MyEntity --limit 10 --offset 20
```

Always check the server code when:
- You're unsure about server's internal APIs and how to interface with them.
- Inner workings of the Space Engineers Dedicated Server is unclear.

## Custom Scripting

For building your own utility scripts to work with the indexes and decompiled code:

- **[ScriptingGuide.md](ScriptingGuide.md)** - How to write Python scripts, use BusyBox, handle Windows paths

## Server Content Data

Textual part of server's `Content` is copied into `Data/Content` folder for free text search:
- Language translations, including string IDs
- Block and other entity definitions
- Default blueprints and scenarios
- See [ContentTypes.md](ContentTypes.md) for full list of content types

### Content Index

`Data/CodeIndex/content_index.csv` maps every textual content file to decompiled C#
source files that reference it. Columns: `rel_path` (path relative to `Data/Content/`)
and `usage` (path of a C# source file in `Data/Decompiled/` that references it). Each
content file appears once per usage, so you can filter and page by `rel_path` to see
all C# code that loads or references a given content file. Files with no known usages
have single row with empty `usage` column.

## Running the Dedicated Server

Server executable is `SpaceEngineersDedicated.exe` in the `DedicatedServer64` folder.

### Headless Mode (No UI)

```
SpaceEngineersDedicated.exe -console
```

Bypasses Telerik WinForms configuration UI and runs server directly.

### Configuration

Server is configured via XML files. Primary configuration file is `SpaceEngineers-Dedicated.cfg` in server's AppData directory (typically `%APPDATA%\SpaceEngineersDedicated\`).

Key configuration areas:
- **Server settings** (name, world, mods, max players)
- **World settings** (game mode, inventory size, welding speed)
- **Network settings** (port, public/private)

Configure by editing XML files directly or with utility Python scripts. See below for planned utilities.

### Planned Utility Scripts (Not Yet Implemented)

- **config_editor.py** — Read and modify `SpaceEngineers-Dedicated.cfg` values from command line (e.g. set server name, max players, world name)
- **world_manager.py** — List, backup, and manage saved worlds in server data directory
- **mod_manager.py** — List and validate mods referenced in configuration

### Server-Only Assemblies

| Assembly | Description |
|----------|-------------|
| `SpaceEngineersDedicated` | Server entry point (replaces `SpaceEngineers.exe`) |
| `VRage.Dedicated` | Dedicated server framework, lifecycle, configuration |
| `VRage.RemoteClient.Core` | Remote client support (RCON-like functionality) |

## General Rules

- In `Data/Decompiled` folder search only inside C# source files (*.cs) in general. If you work on transpiler or preloader patches, then also search IL code (*.il) files.
- In `Data/Content` folder search files appropriate for the task. See [ContentTypes.md](ContentTypes.md) for list of types.
- Do not search for decompiled server code outside `Data/Decompiled` folder. Decompiled server source tree must be there if preparation succeeded.
- Do not search for server content data outside `Data/Content` folder. Copied server content must be there if preparation succeeded.

## Action References

Follow detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
- [search action](./actions/search.md) - Running code searches
- [test action](./actions/test.md) - Testing this skill

## Remarks

Original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
