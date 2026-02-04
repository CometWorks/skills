---
name: se-dev-mod
description: Mod development for Space Engineers version 1
argument-hint: prepare | bash 
license: MIT
---

# SE Dev Mod Skill

Mod development for Space Engineers version 1.

**Actions:**

- **prepare**: Run the one-time preparation (Prepare.bat)
- **bash**: Run UNIX shell commands via busybox

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-mod` | Show this help |
| 2 | Prepare keywords | `se-dev-mod prepare`, `se-dev-mod setup`, `se-dev-mod init` | prepare |
| 3 | Bash/shell keywords | `se-dev-mod bash`, `se-dev-mod grep`, `se-dev-mod find` | bash |

## Getting Started

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps first. See the [prepare action](./actions/prepare.md).

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

## Action References

Follow the detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
