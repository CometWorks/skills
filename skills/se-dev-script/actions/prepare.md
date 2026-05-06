# Prepare Action

> **Part of the se-dev-script skill.** Invoked to run the one-time preparation.

**⚠️ IMPORTANT: Read [CommandExecution.md](../CommandExecution.md) for complete guidance on running commands correctly.**

Run `Prepare.bat` on Windows or `prepare.sh` on Linux to set up the skill environment. This is required before using the skill.

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

1. Review the requirements and instructions in [Prepare.md](../Prepare.md).
2. Execute preparation using the skill folder as working directory:

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
- How to use the workdir parameter correctly
- Common mistakes and how to avoid them

## Critical Rules

- **DO NOT** create the `Prepare.DONE` file yourself.
- It is automatically created by the preparation script only upon a successful run.
- Creating it manually is "faking" success and will lead to errors.

## What Preparation Does

The preparation script:
- Verifies Python ≥ 3.11 and installs `uv` if needed.
- Sets up the Python virtual environment via `uv sync`.
- On Windows downloads `busybox.exe` for UNIX-style shell commands. On Linux uses the native shell tools.
- Creates `Data/` as a junction to `%USERPROFILE%\.se-dev\script` so persistent
  data (script inventory, hashes, code index) lives outside the skill folder.
- Creates `LocalScripts/` as a junction to `%AppData%\SpaceEngineers\IngameScripts\local`.
- Runs `list_scripts.py` to refresh `Data/scripts.json` (cheap; safe to rerun).
- Runs `index_scripts.py` to (incrementally) rebuild `Data/CodeIndex/`.
  Only scripts whose .cs content has changed since the last run are reparsed.

The Steam Workshop content folder is **not** symlinked into the skill —
it is read in-place via the path resolved from `SE_GAME_ROOT` or the
Steam registry entry. PB scripts are detected by the presence of a
top-level `Script.cs` file inside each numeric workshop folder.
