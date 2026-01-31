---
name: se-dev-mod
description: Mod development for Space Engineers version 1
license: MIT
---
## Getting Started

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps:
1. Review the requirements and instructions in [Prepare.md](Prepare.md).
2. Execute the preparation by running `.\Prepare.bat` from this folder.
3. **IMPORTANT:** You are on Windows. Use `&` to chain commands in `cmd.exe` or `;` in PowerShell. Do NOT use `&&`.
4. **DO NOT** create the `Prepare.DONE` file yourself. It is automatically created by `Prepare.bat` only upon a successful run. Creating it manually is "faking" success and will lead to errors.

## Usage Guide
- A Python virtual environment in this folder was made available by the preparation.
- Use this Python virtual environment to write short, targeted, reusable utility scripts as needed. 
  Build a catalog of such scripts in [UtilityScripts.md](UtilityScripts.md) next to this skill file. 
- Use `uv run script_name.py` in this folder (as CWD) to run your scripts.
- **IMPORTANT: Space Engineers modding is done on Windows.** All commands must work on Windows.
- Use `busybox.exe` as a prefix to run individual UNIX-like commands, for example: `busybox.exe grep -r "pattern" folder`.
- Do NOT open a bash shell with `busybox bash`. Run busybox commands directly from cmd or PowerShell instead.
- **CRITICAL: Always use forward slashes (`/`) in file paths passed to busybox.** Backslashes are interpreted as escape characters by bash and will be silently removed, mangling paths. Windows accepts forward slashes. Correct: `busybox.exe grep "pattern" C:/Users/name/folder` — Wrong: `C:\Users\name\folder`.
- Alternatively use Windows PowerShell, which handles backslash paths natively.
- See the list of available Python packages in `pyproject.toml`.
- The `SteamMods` folder contains game content (mods, scripts, blueprints) the player downloaded. Filter mods by the existence of a non-empty `Data/Scripts` folder inside the numbered content folder. 
- The `LocalMods` folder contains mods the player is developing. It is a link to `%AppData%/SpaceEngineers/Mods`.

Use only names matching the Mod API whitelist: [ModApiWhitelist.txt](ModApiWhitelist.txt)
The whitelist was exported from game version `1.208.015` using MDK2's `Mdk.Extractor`.

Mods are released on the Steam Workshop or Mod.IO, mostly on the former.
Mods are compiled by the game on world loading with a Mod API whitelist enforced,
which is supposed to guarantee safety and security. Mods may still crash the game with an exception.

Use the `se-dev-game-code` skill to search the game's decompiled code. You may need this to
understand how the game's internals work and how to interface with it properly. Stick to
game code searches corresponding to names on the Mod API whitelist for efficiency.

References:
- [Mod Template repo](https://github.com/viktor-ferenczi/se-mod-template) Mod template repository to start a new mod project which will include scripts. See [ModTemplate.md](ModTemplate.md)
- [Mod API for script mods](https://malforge.github.io/spaceengineers/modapi/index.html) Structured Mod API documentation
- [Mod API documentation by Keen Software House](https://github.com/KeenSoftwareHouse/SpaceEngineersModAPI) May be outdated
- [Mod Development Kit (MDK2)](https://github.com/malforge/mdk2) Mod development tooling mostly for VS2022