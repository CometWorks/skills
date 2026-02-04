# Prepare Action

> **Part of the se-dev-game-code skill.** Invoked to run the one-time preparation.

Run `Prepare.bat` to set up the skill environment. This is required before using the skill.

## Checking Status

Check if preparation is complete:

```cmd
if exist Prepare.DONE (echo READY) else (echo NOT_READY)
```

Or using bash-compatible syntax:
```bash
test -f "Prepare.DONE" && echo READY || echo NOT_READY
```

## Running Preparation

If `Prepare.DONE` is missing:

1. Review the requirements and instructions in [Prepare.md](../Prepare.md).
2. Execute the preparation by running `.\Prepare.bat` from this folder.
3. **IMPORTANT:** You are on Windows. Use `&` to chain commands in `cmd.exe` or `;` in PowerShell. Do NOT use `&&`.

## Critical Rules

- **DO NOT** create the `Prepare.DONE` file yourself.
- It is automatically created by `Prepare.bat` only upon a successful run.
- Creating it manually is "faking" success and will lead to errors.

## What Preparation Does

The preparation script:
- Sets up the Python virtual environment
- Downloads and installs required tools (busybox.exe, ILSpy)
- Decompiles the game DLLs to C# and IL code
- Builds the code search index
- Copies game content data
- Verifies the environment is ready for use
