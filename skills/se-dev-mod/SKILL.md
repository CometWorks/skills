---
name: se-dev-mod
description: Mod development for Space Engineers version 1. Search mod code for examples and patterns.
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*prepare.sh*), Bash(*Clean.bat*), Bash(*uv run search_mods.py *), Bash(*uv run list_mods.py*), Bash(*uv run index_mods.py*), Bash(command -v graphify*), Bash(graphify*), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Mod Skill

Mod development for Space Engineers version 1.

**⚠️ CRITICAL: Commands run in a UNIX shell. Use bash syntax. On Windows this is BusyBox; on Linux use the native shell.**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - This will NOT work

**Actions:**

- **prepare**: Run one-time preparation (`Prepare.bat` on Windows, `prepare.sh` on Linux)
- **bash**: Run UNIX shell commands via busybox
- **search**: Search mod code using `search_mods.py`

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-mod` | Show this help |
| 2 | Prepare keywords | `se-dev-mod prepare`, `se-dev-mod setup`, `se-dev-mod init` | prepare |
| 3 | Bash/shell keywords | `se-dev-mod bash`, `se-dev-mod grep`, `se-dev-mod cat` | bash |
| 4 | Search keywords | `se-dev-mod search`, `se-dev-mod find class`, `se-dev-mod lookup` | search |

## Getting Started

**⚠️ CRITICAL: Before running ANY commands, read [CommandExecution.md](CommandExecution.md) to avoid common mistakes that cause command failures.**

If `Prepare.DONE` file is missing in this folder, you MUST run one-time preparation steps first. See [prepare action](./actions/prepare.md).

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - Windows command execution details; on Linux keep bash syntax and use `prepare.sh`

## Mod Development

Use only names matching Mod API whitelist: [ModApiWhitelist.txt](ModApiWhitelist.txt)
Whitelist exported from game version `1.208.015` using MDK2's `Mdk.Extractor`.

Mods released on Steam Workshop or Mod.IO, mostly the former.
Game compiles mods on world loading with Mod API whitelist enforced,
supposed to guarantee safety and security. Mods may still crash game with an exception.

Use `se-dev-game-code` skill to search game's decompiled code. May need this to
understand how game's internals work and how to interface with it properly. Stick to
game code searches corresponding to names on Mod API whitelist for efficiency.

## Prepare-Time Graphify Graph

Preparation can build a separate Graphify graph for the local mod folder, or for
`SE_DEV_MOD_PROJECT_ROOT` when set. See
[Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).

## Folder Structure

- `Data/` — junction/symlink to per-user persistent mod data folder (`%USERPROFILE%\.se-dev\mod` on Windows, `~/.se-dev/mod` on Linux). Persistent skill data lives here:
  - `Data/mods.json` — quick inventory of all installed mods (workshop_id, path, has_scripts, ...).
  - `Data/mod_hashes.json` — per-mod aggregate sha1 used by indexer for change detection.
  - `Data/CodeIndex/` — full Tree-sitter C# index (one CSV per category, plus hierarchy trees).
- `LocalMods/` — junction/symlink to game's local-mod folder (`%AppData%\SpaceEngineers\Mods` on Windows, Proton appdata equivalent on Linux).
- Steam Workshop content read in-place from Steam folder; **not copied or symlinked**
  into skill. Workshop folder resolved from `SE_GAME_ROOT` (env var) or Steam
  registry entry for app id 244850.

## References

- [Mod Template repo](https://github.com/viktor-ferenczi/se-mod-template) Mod template repository to start a new mod project which will include scripts. See [ModTemplate.md](ModTemplate.md)
- [Mod API for script mods](https://malforge.github.io/spaceengineers/modapi/index.html) Structured Mod API documentation
- [Mod API documentation by Keen Software House](https://github.com/KeenSoftwareHouse/SpaceEngineersModAPI) May be outdated
- [Mod Development Kit (MDK2)](https://github.com/malforge/mdk2) Mod development tooling mostly for VS2022

## Mod Code Search

Search source code of Steam and local mods for examples and patterns:

```bash
# Search for patterns
uv run search_mods.py class declaration MyBlock
uv run search_mods.py method usage Update
uv run search_mods.py class children MyGameLogicComponent

# Count results before viewing (useful for large result sets)
uv run search_mods.py class usage Init --count

# Limit number of results
uv run search_mods.py class usage Init --limit 10
```

Before searching, ensure index exists. If `Data/CodeIndex/` missing, run:
```bash
uv run list_mods.py     # quick inventory (always cheap)
uv run index_mods.py    # full code index (incremental: only changed mods reparsed)
```

**Re-indexing after new subscriptions:** When you subscribe to new mods on Steam Workshop,
load them in a world once (so game downloads them), then re-run the two commands above
(or just `Prepare.bat`). Indexer hashes each mod's .cs files and only reparses mods
whose hash changed since previous run, so reruns are fast.

See [search action](./actions/search.md) for complete documentation.

## Action References

Follow detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
- [search action](./actions/search.md) - Search mod code for examples

## Remarks

Original source of this skill: https://github.com/CometWorks/skills
