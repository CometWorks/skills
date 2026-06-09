# Prepare Action

> **Part of the se-dev-plugin skill.** Invoked to run the one-time preparation.

**⚠️ IMPORTANT: Read [CommandExecution.md](../CommandExecution.md) for full guidance on running commands correctly.**

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

- **DO NOT** create the `Prepare.DONE` file yourself.
- Automatically created by preparation script only upon successful run.
- Creating it manually is "faking" success and leads to errors.

## What Preparation Does

The preparation script:
- Sets up Python virtual environment
- On Windows downloads `busybox.exe`. On Linux uses native shell tools.
- Downloads plugin sources for examples (to OS temp folder or configured location)
- Verifies environment ready for use
