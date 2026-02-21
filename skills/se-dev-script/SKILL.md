---
name: se-dev-script
description: In-game (programmable block, aka PB) script development for Space Engineers version 1. Search script code for examples and patterns.
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*Clean.bat*), Bash(*run_prepare.sh*), Bash(*uv run search_scripts.py *), Bash(*uv run index_scripts.py*), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Script Skill

In-game (programmable block, aka PB) script development for Space Engineers version 1.

**⚠️ CRITICAL: Commands run in a UNIX shell (busybox), NOT Windows CMD. Use bash syntax!**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - This will NOT work

**Actions:**

- **prepare**: Run the one-time preparation (Prepare.bat)
- **bash**: Run UNIX shell commands via busybox
- **search**: Search script code using `search_scripts.py`

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-script` | Show this help |
| 2 | Prepare keywords | `se-dev-script prepare`, `se-dev-script setup`, `se-dev-script init` | prepare |
| 3 | Bash/shell keywords | `se-dev-script bash`, `se-dev-script grep`, `se-dev-script cat` | bash |
| 4 | Search keywords | `se-dev-script search`, `se-dev-script find class`, `se-dev-script lookup` | search |

## Getting Started

**⚠️ CRITICAL: Before running ANY commands, read [CommandExecution.md](CommandExecution.md) to avoid common mistakes that cause command failures.**

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps first. See the [prepare action](./actions/prepare.md).

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - How to run commands correctly on Windows

## Script Development

Use only names matching the PB API whitelist: [PBApiWhitelist.txt](PBApiWhitelist.txt)
The whitelist was exported from game version `1.208.015` using MDK2's `Mdk.Extractor`.

In-game (PB) scripts are released on the Steam Workshop or Mod.IO, mostly on the former.
In-game scripts are compiled by the game on loading into the PB or world loading (if the PB has a script loaded)
with a PB Script API whitelist enforced, which is supposed to guarantee safety and security.
Scripts cannot crash the game, since any exception is caught and the script is killed by the game.
Scripts can still lag the game if no specific resource usage enforcement is set up by the player or server admin.

The script's source code size is limited to 100,000 bytes when the player loads it. The ScriptDev plugin can load
more from local file into offline (local) games for testing purposes, therefore scripts can be tested without
source code compression, which is useful to get fully detailed exception tracebacks.

Use the `se-dev-game-code` skill to search the game's decompiled code. You may need this to
understand how the game's internals work and how to script it properly. Stick to game code
searches corresponding to names on the PB API whitelist for efficiency.

## Folder Structure

- `SteamScripts` - Game content (mods, scripts, blueprints) the player downloaded. Filter scripts by the existence of a `Script.cs` file directly in the numbered content folder.
- `LocalScripts` - Mods the player is developing. Link to `%AppData%/SpaceEngineers/IngameScripts`.

## References

- [Script Template repo](https://github.com/viktor-ferenczi/se-script-template) PB script template repository to start a new project. See [ScriptTemplate.md](ScriptTemplate.md)
- [Script Merge tool](https://github.com/viktor-ferenczi/se-script-merge) Merging PB scripts from C# projects into single file with optional code compression. See [ScriptMerge.md](ScriptMerge.md)
- [Script Dev plugin](https://github.com/viktor-ferenczi/se-script-dev) Automatic script loading into the PB in-game for easier testing. See [ScriptDev.md](ScriptDev.md)
- [Mod Development Kit (MDK2)](https://github.com/malforge/mdk2)
- [Programmable Block API](https://malforge.github.io/spaceengineers/pbapi)
- [Wiki on Scripting](https://spaceengineers.wiki.gg/wiki/Scripting)

## Script Code Search

Search the source code of Steam and local PB scripts for examples and patterns:

```bash
# Search for patterns
uv run search_scripts.py class declaration Program
uv run search_scripts.py method usage Main
uv run search_scripts.py class children MyGridProgram

# Count results before viewing (useful for large result sets)
uv run search_scripts.py class usage Program --count

# Limit number of results
uv run search_scripts.py class usage GridTerminalSystem --limit 30
```

Before searching, ensure the index exists. If `ScriptCodeIndex/` is missing, run:
```bash
uv run index_scripts.py
```

**Re-indexing after new subscriptions:** When you subscribe to new scripts on Steam Workshop,
load them in a world once (so the game downloads them), then re-run `uv run index_scripts.py`
to make the new script code available for search.

See [search action](./actions/search.md) for complete documentation.

## Action References

Follow the detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
- [search action](./actions/search.md) - Search script code for examples

## Remarks

The original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
