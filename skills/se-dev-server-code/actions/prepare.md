# Prepare Action

> **Part of the se-dev-server-code skill.** Invoked to run the one-time preparation.

**⚠️ IMPORTANT: Read [CommandExecution.md](../CommandExecution.md) for complete guidance on running commands correctly.**

Run `Prepare.bat` on Windows or `prepare.sh` on Linux to set up skill environment. Required before using skill.

## Quick Check Status

**IMPORTANT**: Use bash syntax, NOT Windows CMD syntax. Commands run through busybox (UNIX shell).

```bash
# ✅ CORRECT - Use bash syntax
test -f "Prepare.DONE" && echo "READY" || echo "NOT_READY"
```

**Alternative**: Use Glob tool to check for file existence instead of bash commands.

```bash
# ❌ WRONG - Don't use Windows CMD syntax (will NOT work)
# if exist Prepare.DONE (echo READY) else (echo NOT_READY)
```

## Running Preparation

If `Prepare.DONE` is missing:

1. Review requirements and instructions in [Prepare.md](../Prepare.md).
2. Execute preparation using skill folder as working directory:

**Recommended (using workdir parameter):**
```bash
./prepare.sh (Linux)
```

If auto-detection fails, set `SE_SERVER_ROOT` first. May point either to dedicated server root or directly to `DedicatedServer64` directory.

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
- Preparation script creates it automatically only upon successful run.
- Creating it manually is "faking" success and leads to errors.

## What Preparation Does

Preparation script:
- Verifies Python 3.11+ and command line `git` client are available
- Sets up Python virtual environment
- On Windows downloads `busybox.exe`. On Linux uses native shell tools.
- Installs `ilspycmd` for decompilation.
- Creates `Data` junction pointing to `%USERPROFILE%\.se-dev\server-code\`
- Initialises local Git repository inside `Data/` on first run (with initial commit of `.gitignore`)
- Detects current server version directly from binaries
- Wipes `Data/Decompiled`, `Data/Content` and `Data/CodeIndex` whenever version differs from recorded one (older versions remain in local Git history)
- Decompiles server DLLs to C# and optionally to IL code (needs uncommenting a line in `DecompileDll.sh` if required)
- Records new server version in `Data/game_version.txt` and commits decompiled sources with version label as commit message
- Copies server content data into `Data/Content`
- Builds code search index in `Data/CodeIndex`
- Verifies environment is ready for use
