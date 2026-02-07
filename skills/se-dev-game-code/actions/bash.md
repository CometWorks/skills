# Bash Action

> **Part of the se-dev-game-code skill.** Invoked when running UNIX shell commands.

**⚠️ IMPORTANT: Read [CommandExecution.md](../CommandExecution.md) for complete guidance on running commands correctly.**

## Quick Reference

Run UNIX-like commands using `busybox.exe` as a prefix:

```bash
busybox.exe grep -r "pattern" folder
busybox.exe find . -name "*.cs"
busybox.exe cat file.txt
```

## Critical Rules (Summary)

1. **ALWAYS use forward slashes (`/`) in paths** when using busybox
   - ✅ Correct: `busybox.exe grep "pattern" C:/Users/name/folder`
   - ❌ Wrong: `busybox.exe grep "pattern" C:\Users\name\folder`

2. **Use the skill folder as working directory**
   - Best approach: Use the `workdir` parameter in your bash tool
   - Alternative: Change to skill folder first, then run commands

3. **Run commands directly** - Don't open an interactive bash shell unless needed

4. **Windows accepts forward slashes natively** - This works everywhere on Windows

## Alternative: Use PowerShell

If busybox doesn't work for a specific task, use PowerShell instead:

```powershell
Get-ChildItem -Recurse -Filter "*.cs" | Select-String "pattern"
```

PowerShell handles backslash paths correctly.

## Complete Documentation

For detailed examples, troubleshooting, and best practices, see:
- **[CommandExecution.md](../CommandExecution.md)** - Complete command execution guide

## Available Commands

BusyBox provides many standard UNIX utilities including:
- `grep` - Search file contents
- `find` - Find files by name/pattern
- `cat`, `head`, `tail` - View file contents
- `sed`, `awk` - Text processing
- `sort`, `uniq` - Sorting and deduplication
- `wc` - Word/line counting
- And many more

Run `busybox.exe --list` to see all available commands.

## Python Virtual Environment

A Python virtual environment is available in this skill folder. Use `uv run script_name.py` to run scripts with the correct environment.

See available packages in `pyproject.toml`.
