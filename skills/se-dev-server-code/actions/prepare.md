# Prepare Action

> **Part of the se-dev-server-code skill.** Invoked to run the one-time preparation.

**⚠️ IMPORTANT: Read [CommandExecution.md](../CommandExecution.md) for complete guidance on running commands correctly.**

Run `Prepare.bat` on Windows or `prepare.sh` on Linux/macOS to set up the skill environment. This is required before using the skill.

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
./prepare.sh (Linux/macOS)
```

If auto-detection fails, set `SE_SERVER_ROOT` first. It may point either to the dedicated server root or directly to the `DedicatedServer64` directory.

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
- Verifies that Python 3.11+ and the command line `git` client are available
- Sets up the Python virtual environment
- On Windows downloads `busybox.exe`. On Linux/macOS uses the native shell tools.
- Installs `ilspycmd` for decompilation.
- Creates the `Data` junction pointing to `%USERPROFILE%\.se-dev\server-code\`
- Initialises a local Git repository inside `Data/` on first run (with an initial commit of `.gitignore`)
- Detects the current server version directly from the binaries
- Wipes `Data/Decompiled`, `Data/Content` and `Data/CodeIndex` whenever the version differs from the recorded one (older versions remain in the local Git history)
- Decompiles the server DLLs to C# and optionally to IL code (needs uncommenting a line in `DecompileDll.sh` if this is required)
- Records the new server version in `Data/game_version.txt` and commits the decompiled sources with the version label as the commit message
- Copies server content data into `Data/Content`
- Builds the code search index in `Data/CodeIndex`
- Verifies the environment is ready for use
