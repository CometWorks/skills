# Prepare Action

> **Part of the se-dev-mod skill.** Invoked to run the one-time preparation.

**⚠️ IMPORTANT: Read [CommandExecution.md](../CommandExecution.md) for complete guidance on running commands correctly.**

Run `Prepare.bat` on Windows or `prepare.sh` on Linux to set up skill environment. Required before using skill.

## Quick Check Status

**IMPORTANT**: Use bash syntax, NOT Windows CMD syntax. Commands run through busybox (UNIX shell).

```bash
# ✅ CORRECT - Use bash syntax
test -f "Prepare.DONE" && echo "READY" || echo "NOT_READY"
```

**Alternative**: Use the Glob tool to check for file existence instead of bash commands.

```bash
# ❌ WRONG - Don't use Windows CMD syntax (will NOT work)
# if exist Prepare.DONE (echo READY) else (echo NOT_READY)
```

## Running Preparation

If `Prepare.DONE` is missing:

1. Review requirements and instructions in [Prepare.md](../Prepare.md).
2. Run preparation using skill folder as working directory:

**Recommended approach (using workdir parameter):**
```bash
./prepare.sh (Linux)
```

**Alternative approaches:**

Using PowerShell:
```powershell
cd C:\path\to\skill\folder
.\Prepare.bat
```

Using CMD (change directory first):
```cmd
cd /d C:\path\to\skill\folder
Prepare.bat
```

**⚠️ CRITICAL:** See [CommandExecution.md](../CommandExecution.md) for details on:
- Why `&&` doesn't work in CMD
- How to use workdir parameter correctly
- Common mistakes and how to avoid them

## Critical Rules

- **DO NOT** create `Prepare.DONE` file yourself.
- Preparation script creates it automatically only on successful run.
- Creating it manually "fakes" success and leads to errors.

## What Preparation Does

Preparation script:
- Verifies Python ≥ 3.11 and installs `uv` if needed.
- Sets up Python virtual environment via `uv sync`.
- On Windows downloads `busybox.exe` for UNIX-style shell commands. On Linux uses native shell tools.
- Creates `Data/` as junction to `%USERPROFILE%\.se-dev\mod` so persistent
  data (mod inventory, hashes, code index) lives outside skill folder.
- Creates `LocalMods/` as junction to `%AppData%\SpaceEngineers\Mods`.
- Runs `list_mods.py` to refresh `Data/mods.json` (cheap; safe to rerun).
- Runs `index_mods.py` to (incrementally) rebuild `Data/CodeIndex/`.
  Only mods whose .cs content changed since last run are reparsed.

Steam Workshop content folder is **not** symlinked into skill —
read in-place via path resolved from `SE_GAME_ROOT` or
Steam registry entry.
