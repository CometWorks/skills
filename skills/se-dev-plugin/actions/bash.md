# Bash Action

> **Part of the se-dev-plugin skill.** Invoked when running UNIX shell commands.

Run UNIX-like commands using `busybox.exe` as a prefix.

## Usage

Run individual UNIX commands directly from cmd or PowerShell:

```cmd
busybox.exe grep -r "pattern" folder
busybox.exe find . -name "*.cs"
busybox.exe cat file.txt
```

## Critical Rules

1. **Do NOT open a bash shell** with `busybox bash`. Run commands directly instead.

2. **Always use forward slashes (`/`) in file paths passed to busybox.** Backslashes are interpreted as escape characters by bash and will be silently removed, mangling paths.

   - Correct: `busybox.exe grep "pattern" C:/Users/name/folder`
   - Wrong: `busybox.exe grep "pattern" C:\Users\name\folder`

3. Windows accepts forward slashes, so this works system-wide.

4. Alternatively use Windows PowerShell, which handles backslash paths natively.

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
