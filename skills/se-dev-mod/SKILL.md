---
name: se-dev-mod
description: Mod development for Space Engineers version 1. Search mod code for examples and patterns.
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*Clean.bat*), Bash(*run_prepare.sh*), Bash(*uv run search_mods.py *), Bash(*uv run index_mods.py*), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Mod Skill

Mod development for Space Engineers version 1.

**⚠️ CRITICAL: Commands run in a UNIX shell (busybox), NOT Windows CMD. Use bash syntax!**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - This will NOT work

**Actions:**

- **prepare**: Run the one-time preparation (Prepare.bat)
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

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps first. See the [prepare action](./actions/prepare.md).

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - How to run commands correctly on Windows

## Mod Development

Use only names matching the Mod API whitelist: [ModApiWhitelist.txt](ModApiWhitelist.txt)
The whitelist was exported from game version `1.208.015` using MDK2's `Mdk.Extractor`.

Mods are released on the Steam Workshop or Mod.IO, mostly on the former.
Mods are compiled by the game on world loading with a Mod API whitelist enforced,
which is supposed to guarantee safety and security. Mods may still crash the game with an exception.

Use the `se-dev-game-code` skill to search the game's decompiled code. You may need this to
understand how the game's internals work and how to interface with it properly. Stick to
game code searches corresponding to names on the Mod API whitelist for efficiency.

## Folder Structure

- `SteamMods` - Game content (mods, scripts, blueprints) the player downloaded. Filter mods by the existence of a non-empty `Data/Scripts` folder inside the numbered content folder.
- `LocalMods` - Mods the player is developing. Link to `%AppData%/SpaceEngineers/Mods`.

## References

- [Mod Template repo](https://github.com/viktor-ferenczi/se-mod-template) Mod template repository to start a new mod project which will include scripts. See [ModTemplate.md](ModTemplate.md)
- [Mod API for script mods](https://malforge.github.io/spaceengineers/modapi/index.html) Structured Mod API documentation
- [Mod API documentation by Keen Software House](https://github.com/KeenSoftwareHouse/SpaceEngineersModAPI) May be outdated
- [Mod Development Kit (MDK2)](https://github.com/malforge/mdk2) Mod development tooling mostly for VS2022

## Mod Code Search

Search the source code of Steam and local mods for examples and patterns:

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

Before searching, ensure the index exists. If `ModCodeIndex/` is missing, run:
```bash
uv run index_mods.py
```

**Re-indexing after new subscriptions:** When you subscribe to new mods on Steam Workshop,
load them in a world once (so the game downloads them), then re-run `uv run index_mods.py`
to make the new mod code available for search.

See [search action](./actions/search.md) for complete documentation.

## Action References

Follow the detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
- [search action](./actions/search.md) - Search mod code for examples

## Remarks

The original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
