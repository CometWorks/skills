# Command Execution - Detailed Guide

This document provides comprehensive details about command execution on Windows for the se-dev-server-code skill. For most use cases, see Quick Start section in [CommandExecution.md](CommandExecution.md).

## Recommended Approach

**Use the skill folder's `workdir` parameter when running bash commands:**

```bash
# RECOMMENDED: Use workdir parameter to run commands in the skill folder
bash -c "./Prepare.bat" (with workdir set to the skill folder)
uv run search_server_code.py class declaration MyCubeGrid (with workdir set to the skill folder)
```

Most reliable approach because:
- No need to manually `cd` to folder
- Works consistently across all shells
- Avoids path and command chaining issues

## Shell Options on Windows

Three shell options on Windows, each with different syntax rules:

### Option 1: BusyBox Bash (Recommended for UNIX commands)

BusyBox provides UNIX-like commands on Windows. Use it for individual commands:

```bash
# Run UNIX commands via busybox.exe
busybox.exe grep -r "pattern" folder
busybox.exe find . -name "*.cs"
busybox.exe cat file.txt
```

**CRITICAL PATH RULE:** Always use forward slashes (`/`) in paths passed to busybox:
- ✅ Correct: `busybox.exe grep "pattern" C:/Users/name/folder`
- ❌ Wrong: `busybox.exe grep "pattern" C:\Users\name\folder` (backslashes are escape characters!)

**DO NOT** open interactive bash shell with `busybox bash` unless needed for a sequence of commands.

### Option 2: PowerShell (Native Windows)

PowerShell is a native Windows shell that handles backslash paths correctly:

```powershell
# PowerShell examples
cd C:\path\to\skill\folder
.\Prepare.bat
uv run search_server_code.py class declaration MyCubeGrid
```

PowerShell uses `;` to chain commands, not `&&`:
```powershell
cd C:\path\to\skill\folder; .\Prepare.bat
```

### Option 3: CMD (Windows Command Prompt) - Not Recommended

CMD is the legacy Windows shell with limited features:

```cmd
REM CMD does NOT support && for command chaining
REM Use & instead, or run commands separately

cd /d C:\path\to\skill\folder
Prepare.bat

REM Or chain with &
cd /d C:\path\to\skill\folder & Prepare.bat
```

**Note:** `&&` does NOT work in CMD. Common source of errors.

## Command Execution Rules - Critical Guidelines

### Rule 1: Choose ONE Shell and Stick With It

**DO NOT mix shell syntaxes.** Once you choose a shell approach, use it consistently:
- If using busybox, use busybox syntax
- If using PowerShell, use PowerShell syntax
- If using CMD, use CMD syntax

### Rule 2: Use the Skill Folder as Working Directory

**Always run commands from skill folder as current working directory (CWD).**

Methods to ensure correct CWD:
1. **Best:** Use `workdir` parameter in bash tool
2. **Alternative:** Change directory first, then run commands separately
3. **Avoid:** Don't chain `cd` with `&&` in CMD

### Rule 3: Verify Preparation Status Before Running Commands

Before using any skill features, check if preparation complete:

**Using bash syntax:**
```bash
test -f "Prepare.DONE" && echo "READY" || echo "NOT_READY"
```

**Using CMD:**
```cmd
if exist Prepare.DONE (echo READY) else (echo NOT_READY)
```

**Using PowerShell:**
```powershell
if (Test-Path "Prepare.DONE") { "READY" } else { "NOT_READY" }
```

### Rule 4: Python Commands Must Use `uv run`

All Python scripts in this skill must run via `uv run`:

```bash
uv run search_server_code.py class declaration MyCubeGrid
uv run index_code.py
```

This ensures correct Python virtual environment is used.

## Common Mistakes and Solutions

### ❌ Mistake 1: Using && in CMD

```cmd
cd C:\skills\se-dev-server-code && Prepare.bat
```
**Error:** `&&` not recognized in CMD

✅ **Solution 1:** Use `&` instead:
```cmd
cd C:\skills\se-dev-server-code & Prepare.bat
```

✅ **Solution 2:** Use separate commands:
```cmd
cd C:\skills\se-dev-server-code
Prepare.bat
```

✅ **Solution 3:** Use PowerShell or workdir parameter instead

### ❌ Mistake 2: Using Backslashes with BusyBox

```bash
busybox.exe grep "pattern" C:\Users\name\folder
```
**Error:** Backslashes interpreted as escape characters, path becomes `C:Usersnamefolder`

✅ **Solution:** Use forward slashes:
```bash
busybox.exe grep "pattern" C:/Users/name/folder
```

### ❌ Mistake 3: Running Commands from Wrong Directory

```cmd
C:\Users\name> uv run search_server_code.py class declaration MyCubeGrid
```
**Error:** `search_server_code.py` not found, wrong CWD

✅ **Solution 1:** Use workdir parameter:
```bash
uv run search_server_code.py class declaration MyCubeGrid (with workdir=C:\path\to\skill\folder)
```

✅ **Solution 2:** Change directory first:
```cmd
cd C:\path\to\skill\folder
uv run search_server_code.py class declaration MyCubeGrid
```

### ❌ Mistake 4: Forgetting to Prepare

```bash
uv run search_server_code.py class declaration MyCubeGrid
```
**Error:** Index files missing, Python environment not set up

✅ **Solution:** Check for `Prepare.DONE`, run `Prepare.bat` if missing:
```bash
# Check status first
test -f "Prepare.DONE" && echo "READY" || echo "NOT_READY"

# If NOT_READY, run preparation
./Prepare.bat
```

## Recommended Workflow for Agents

**Step 1:** Verify skill folder exists and is accessible

**Step 2:** Check preparation status by looking for `Prepare.DONE` file

**Step 3:** If not prepared, run `Prepare.bat` using workdir parameter:
```bash
./Prepare.bat (with workdir set to skill folder)
```

**Step 4:** Once prepared, run commands using workdir parameter:
```bash
uv run search_server_code.py class declaration MyCubeGrid (with workdir set to skill folder)
```

**Step 5:** For UNIX commands, use busybox with forward slashes:
```bash
busybox.exe grep -r "MyCubeGrid" C:/path/to/Data/Decompiled
```

## Troubleshooting Checklist

**If a command fails, verify:**

1. ✓ **Correct working directory?**
   - Run `pwd` (bash) or `cd` (CMD/PowerShell) to check
   - Skill commands must run from skill folder

2. ✓ **Correct shell syntax?**
   - CMD doesn't support `&&` → use `&` or PowerShell
   - BusyBox needs forward slashes `/` in paths
   - Don't mix shell syntaxes

3. ✓ **Preparation complete?**
   - Check for `Prepare.DONE` file in skill folder
   - If missing, run `Prepare.bat` first

4. ✓ **Correct command format?**
   - Python scripts: `uv run script.py`
   - BusyBox commands: `busybox.exe command`
   - Batch files: `.\Prepare.bat` or just `Prepare.bat`

5. ✓ **Quoting correct?**
   - Use quotes for arguments with spaces
   - Use quotes for regex patterns with special characters

## Advanced: Running Multiple Commands

**To run a sequence of commands:**

**Option A:** Use workdir parameter for each command (recommended):
```bash
# Command 1
./Prepare.bat (workdir: skill_folder)
# Command 2
uv run search_server_code.py class declaration MyCubeGrid (workdir: skill_folder)
```

**Option B:** Use PowerShell with semicolons:
```powershell
cd C:\path\to\skill; .\Prepare.bat; uv run search_server_code.py class declaration MyCubeGrid
```


## Summary

**Key takeaways:**
1. Use workdir parameter when running commands - most reliable
2. If using BusyBox, always use forward slashes in paths
3. Don't use `&&` in CMD - use `&` or PowerShell instead
4. Always run from skill folder as CWD
5. Check for `Prepare.DONE` before using skill features
6. Use `uv run` for all Python scripts

Following these rules eliminates command execution errors and makes agent interactions smooth and reliable.
