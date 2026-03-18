# Search Action

> **Part of the se-dev-mod skill.** Invoked when searching mod source code.

Search mod code using `uv run search_mods.py` from this skill folder.

## Prerequisites

Before searching, ensure the mod code index exists. If `ModCodeIndex/` directory is missing, run:

```cmd
uv run index_mods.py
```

This indexes all mods from:
- `SteamMods/` - Downloaded mods from Steam Workshop (folders with `Data/Scripts` subdirectory)
- `LocalMods/` - Local development mods

## Quick Reference

```cmd
uv run search_mods.py --help
```

## Search Syntax

```cmd
uv run search_mods.py <category> <symbol_type> <pattern> [options]
```

### Categories
- `class` - Classes and records
- `interface` - Interfaces
- `struct` - Structs
- `enum` - Enums
- `method` - Methods
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
uv run search_mods.py class declaration MyBlock
```

### Find method usages
```cmd
uv run search_mods.py method usage Update
```

### Find method signatures
```cmd
uv run search_mods.py method signature Init
```

### Find children of a base class
```cmd
uv run search_mods.py class children MyGameLogicComponent
```

### Find implementations of an interface
```cmd
uv run search_mods.py interface implementors IMyTerminalBlock

```

### Filter by namespace
```cmd
uv run search_mods.py class declaration -n "MyMod" Block
```

### Case-insensitive search
```cmd
uv run search_mods.py -i class declaration player
```

## Mod List

After indexing, the list of discovered mods is saved to `ModCodeIndex/mods.json`. This file contains information about each mod including its source (steam/local) and path.

## When to Search

Search mod code when:
- Looking for examples of how other mods implement specific features
- Understanding patterns used in mod development
- Finding usage examples of game APIs in real mods
