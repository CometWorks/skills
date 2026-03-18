# Search Action

> **Part of the se-dev-script skill.** Invoked when searching PB script source code.

Search PB script code using `uv run search_scripts.py` from this skill folder.

## Prerequisites

Before searching, ensure the script code index exists. If `ScriptCodeIndex/` directory is missing, run:

```cmd
uv run index_scripts.py
```

This indexes all scripts from:
- `SteamScripts/` - Downloaded scripts from Steam Workshop (folders with `Script.cs` file)
- `LocalScripts/` - Local development scripts

## Quick Reference

```cmd
uv run search_scripts.py --help
```

## Search Syntax

```cmd
uv run search_scripts.py <category> <symbol_type> <pattern> [options]
```

### Categories
- `class` - Classes and records
- `interface` - Interfaces
- `struct` - Structs
- `enum` - Enums
- `method` - Methods (excluding constructors)
- `field` - Fields (member variables)
- `property` - Properties
- `event` - Events
- `constructor` - Constructors
- `namespace` - Namespaces

### Symbol Types
- `declaration` - Where symbols are defined
- `usage` - Where symbols are used
- `signature` - Method signatures (method category only)
- `parent` - Parent class/interface (class/interface categories)
- `children` - Child classes/interfaces (class/interface categories)
- `implements` - Interfaces implemented by a class (class category)
- `implementors` - Classes implementing an interface (interface category)

### Options
- `-c, --count` - Print only the count of matches
- `-l, --limit N` - Limit number of results
- `-o, --offset N` - Skip first N results
- `-n, --namespace PREFIX` - Filter by namespace prefix
- `-i, --case-insensitive` - Case-insensitive matching

### Patterns
- `text:X` or just `X` - Literal text match
- `re:X` - Regular expression match

## Examples

### Find class declarations
```cmd
uv run search_scripts.py class declaration Program
```

### Find method usages
```cmd
uv run search_scripts.py method usage Main
```

### Find method signatures
```cmd
uv run search_scripts.py method signature Save
```

### Find children of MyGridProgram
```cmd
uv run search_scripts.py class children MyGridProgram
```

### Case-insensitive search
```cmd
uv run search_scripts.py -i class declaration inventory
```

## Script List

After indexing, the list of discovered scripts is saved to `ScriptCodeIndex/scripts.json`. This file contains information about each script including its source (steam/local) and path.

## When to Search

Search script code when:
- Looking for examples of how other scripts implement specific features
- Understanding patterns used in PB script development
- Finding usage examples of the PB API in real scripts
