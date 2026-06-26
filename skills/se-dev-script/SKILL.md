---
name: se-dev-script
description: In-game (programmable block, aka PB) script development for Space Engineers version 1. Search script code for examples and patterns.
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*prepare.sh*), Bash(*Clean.bat*), Bash(*uv run search_scripts.py *), Bash(*uv run list_scripts.py*), Bash(*uv run index_scripts.py*), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Script Skill

In-game (programmable block, aka PB) script development for Space Engineers version 1.

**⚠️ CRITICAL: Commands run in UNIX shell. Use bash syntax. On Windows this is BusyBox; on Linux use native shell.**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - Will NOT work

**Actions:**

- **prepare**: Run one-time preparation (`Prepare.bat` on Windows, `prepare.sh` on Linux)
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

If `Prepare.DONE` file missing in this folder, you MUST run one-time preparation steps first. See the [prepare action](./actions/prepare.md).

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - Windows command execution details; on Linux keep bash syntax and use `prepare.sh`

## Script Development

Use only names matching the PB API whitelist: [PBApiWhitelist.txt](PBApiWhitelist.txt)
Whitelist was exported from game version `1.208.015` using MDK2's `Mdk.Extractor`.

In-game (PB) scripts released on Steam Workshop or Mod.IO, mostly on former.
In-game scripts compiled by game on loading into PB or world loading (if PB has script loaded)
with PB Script API whitelist enforced, which guarantees safety and security.
Scripts cannot crash game, since any exception caught and script killed by game.
Scripts can still lag game if no specific resource usage enforcement set up by player or server admin.

Script's source code size limited to 100,000 bytes when player loads it. ScriptDev plugin can load
more from local file into offline (local) games for testing, so scripts can be tested without
source code compression, useful to get fully detailed exception tracebacks.

Use the `se-dev-game-code` skill to search game's decompiled code. You may need this to
understand how game's internals work and how to script it properly. Stick to game code
searches corresponding to names on PB API whitelist for efficiency.

## Folder Structure

- `Data/` — junction/symlink to per-user persistent script data folder (`%USERPROFILE%\.se-dev\script` on Windows, `~/.se-dev/script` on Linux). Persistent skill data lives here:
  - `Data/scripts.json` — quick inventory of all installed PB scripts.
  - `Data/script_hashes.json` — per-script aggregate sha1 used by indexer for change detection.
  - `Data/CodeIndex/` — full Tree-sitter C# index (one CSV per category, plus hierarchy trees).
- `LocalScripts/` — junction/symlink to game's local-script folder (`%AppData%\SpaceEngineers\IngameScripts\local` on Windows, Proton appdata equivalent on Linux),
  game's local-PB-script folder.
- Steam Workshop content read in-place from Steam folder; **it is not copied or symlinked**
  into skill. PB scripts detected by presence of top-level `Script.cs` file
  inside each numeric workshop folder. Workshop folder resolved from `SE_GAME_ROOT`
  (env var) or Steam registry entry for app id 244850.

## References

- [Script Template repo](https://github.com/viktor-ferenczi/se-script-template) PB script template repository to start new project. See [ScriptTemplate.md](ScriptTemplate.md)
- [Script Merge tool](https://github.com/viktor-ferenczi/se-script-merge) Merging PB scripts from C# projects into single file with optional code compression. See [ScriptMerge.md](ScriptMerge.md)
- [Script Dev plugin](https://github.com/viktor-ferenczi/se-script-dev) Automatic script loading into PB in-game for easier testing. See [ScriptDev.md](ScriptDev.md)
- [Mod Development Kit (MDK2)](https://github.com/malforge/mdk2)
- [Programmable Block API](https://malforge.github.io/spaceengineers/pbapi)
- [Wiki on Scripting](https://spaceengineers.wiki.gg/wiki/Scripting)

## Script Code Search

Search source code of Steam and local PB scripts for examples and patterns:

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

Before searching, ensure index exists. If `Data/CodeIndex/` missing, run:
```bash
uv run list_scripts.py     # quick inventory (always cheap)
uv run index_scripts.py    # full code index (incremental: only changed scripts reparsed)
```

**Re-indexing after new subscriptions:** When you subscribe to new scripts on Steam Workshop,
load them in world once (so game downloads them), then re-run the two commands above
(or `Prepare.bat`). Indexer hashes each script's .cs files and only reparses
scripts whose hash changed since previous run, so reruns are fast.

See [search action](./actions/search.md) for complete documentation.

## Action References

Follow the detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
- [search action](./actions/search.md) - Search script code for examples

## Remarks

Original source of this skill: https://github.com/CometWorks/skills
