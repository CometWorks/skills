# Custom Scripting Guide

How to build custom utility scripts to work with the decompiled code and indexes.

## Python Environment

A Python virtual environment in this folder was made available by the preparation process.

- Use this environment to write short, targeted, reusable utility scripts
- Build a catalog of scripts in `UtilityScripts.md` next to this file
- Run scripts with: `uv run script_name.py` (from this folder as CWD)
- See available Python packages in `pyproject.toml`

## Windows Command Line Guidelines

**IMPORTANT:** Space Engineers modding is done on Windows. All commands must work on Windows.

### Using BusyBox

BusyBox provides UNIX-like commands on Windows:

```bash
# Run individual commands with busybox.exe prefix
busybox.exe grep -r "pattern" folder
busybox.exe find . -name "*.cs"
busybox.exe sed -i 's/old/new/g' file.txt
```

**DO NOT** open a bash shell with `busybox bash`. Run commands directly from cmd or PowerShell instead.

### Critical: Path Handling

**CRITICAL:** Always use forward slashes (`/`) in file paths passed to busybox.

- Backslashes are interpreted as escape characters by bash
- Backslashes will be silently removed, mangling paths
- Windows accepts forward slashes natively

**Correct:**
```bash
busybox.exe grep "pattern" C:/Users/name/folder
busybox.exe find C:/Dev/SE1/Skills/se-dev-skills -name "*.cs"
```

**Wrong:**
```bash
busybox.exe grep "pattern" C:\Users\name\folder
# Backslashes will be removed, path becomes: C:Usersnamesolder
```

### Using PowerShell Instead

Alternatively, use Windows PowerShell which handles backslash paths natively:

```powershell
Get-ChildItem -Recurse -Filter "*.cs" | Select-String "pattern"
```

## Scripting Best Practices

1. **Keep scripts focused** - One task per script
2. **Document in UtilityScripts.md** - Add entries as you create scripts
3. **Use the indexes** - Leverage existing CSV files instead of parsing source
4. **Handle paths correctly** - Follow the guidelines above
5. **Test on Windows** - Always verify scripts work on Windows

## Example Scripts

### Simple Index Query

```python
#!/usr/bin/env python3
import csv
from pathlib import Path

INDEX_DIR = Path(__file__).parent / "CodeIndex"

def find_methods_in_class(class_name):
    """Find all methods declared in a specific class"""
    with open(INDEX_DIR / "method_declarations.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["declaring_type"] == class_name:
                print(f"{row['method']} at {row['file_path']}:{row['start_line']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: uv run script.py <class_name>")
        sys.exit(1)
    find_methods_in_class(sys.argv[1])
```

### Using BusyBox in Python

```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

def grep_decompiled(pattern):
    """Search decompiled source using busybox grep"""
    # Use forward slashes for paths
    decompiled = Path("Decompiled").resolve().as_posix()
    
    result = subprocess.run(
        ["busybox.exe", "grep", "-r", "-n", pattern, decompiled],
        capture_output=True,
        text=True
    )
    
    return result.stdout

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: uv run script.py <pattern>")
        sys.exit(1)
    print(grep_decompiled(sys.argv[1]))
```

## Common Tasks

### Working with CSV Indexes

All index files are in `CodeIndex/` directory. Use Python's `csv` module:

```python
import csv

with open("CodeIndex/class_declarations.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # row is a dict with columns as keys
        print(row["namespace"], row["declaring_type"])
```

### Reading Decompiled Source

Files are in `Decompiled/` directory:

```python
from pathlib import Path

# From search result: VRage.Math/VRageMath/Vector3D.cs:13-2293
file_path = Path("Decompiled/VRage.Math/VRageMath/Vector3D.cs")

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    # Lines are 0-indexed, search results are 1-indexed
    code_snippet = lines[12:2293]  # Lines 13-2293
```

### Searching Content Data

Game content is in `Content/` directory. See `ContentTypes.md` for structure.

```python
from pathlib import Path

# Search all SBC files
for sbc_file in Path("Content/Data").rglob("*.sbc"):
    with open(sbc_file, "r", encoding="utf-8") as f:
        content = f.read()
        if "LargeBlockArmorBlock" in content:
            print(f"Found in: {sbc_file}")
```

## See Also

- **UtilityScripts.md** - Catalog of available utility scripts
- **Implementation.md** - Technical details on index formats
- **pyproject.toml** - Available Python packages
