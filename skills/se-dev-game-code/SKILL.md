---
name: se-dev-game-code
description: Allows reading the decompiled C# code of Space Engineers version 1.  
license: MIT
---

## Getting Started

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps:
1. Review the requirements and instructions in [Prepare.md](Prepare.md).
2. Execute the preparation by running `.\Prepare.bat` from this folder.
3. **IMPORTANT:** You are on Windows. Use `&` to chain commands in `cmd.exe` or `;` in PowerShell. Do NOT use `&&`.
4. **DO NOT** create the `Prepare.DONE` file yourself. It is automatically created by `Prepare.bat` only upon a successful run. Creating it manually is "faking" success and will lead to errors.

To check if preparation is complete, use bash-compatible syntax:
```bash
test -f "C:\Users\viktor\.claude\skills\se-dev-game-code\Prepare.DONE" && echo READY || echo NOT_READY
```

## Code Search - Quick Reference

Run searches from this skill folder using `uv run search_code.py`:

Run `uv run search_code.py --help` to see its basic usage.

## Code Search Documentation

- **[QuickStart.md](QuickStart.md)** - More examples and quick reference
- **[CodeSearch.md](CodeSearch.md)** - Complete guide to searching classes, methods, fields, etc.
- **[HierarchySearch.md](HierarchySearch.md)** - Finding class/interface inheritance and implementations
- **[Advanced.md](Advanced.md)** - Power user techniques for complex searches
- **[Implementation.md](Implementation.md)** - Technical details for skill contributors (optional)

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
