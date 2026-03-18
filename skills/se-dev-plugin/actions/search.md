# Search Action

> **Part of the se-dev-plugin skill.** Invoked when searching plugin source code.

Search plugin code using `uv run search_plugins.py` from this skill folder.

## Prerequisites

### 1. Update PluginHub (optional but recommended)

```cmd
uv run download_pluginhub.py
```

This downloads/updates the PluginHub registry with all available plugins.

### 2. List Available Plugins

```cmd
uv run list_plugins.py                    # List all plugins
uv run list_plugins.py --local            # List only locally available plugins
uv run list_plugins.py --search "camera"  # Search plugins by name/description
uv run list_plugins.py -v                 # Verbose output with descriptions
```

### 3. Download Plugin Source

```cmd
uv run download_plugin_source.py "Tool Switcher"
uv run download_plugin_source.py austinvaness/ToolSwitcherPlugin
uv run download_plugin_source.py ToolSwitcherPlugin
```

### 4. Index Downloaded Plugins

```cmd
uv run index_plugins.py
```

This indexes all downloaded plugin source code.

## Quick Reference

```cmd
uv run search_plugins.py --help
```

## Search Syntax

```cmd
uv run search_plugins.py <category> <symbol_type> <pattern> [options]
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
uv run search_plugins.py class declaration Plugin
```

### Find Harmony patch methods
```cmd
uv run search_plugins.py method declaration Patch
uv run search_plugins.py method signature Prefix
uv run search_plugins.py method signature Postfix
```

### Find method usages
```cmd
uv run search_plugins.py method usage Harmony
```

### Find children of a base class
```cmd
uv run search_plugins.py class children PluginBase
```

### Case-insensitive search
```cmd
uv run search_plugins.py -i class declaration config
```

## Plugin List

After indexing, `PluginCodeIndex/plugins.json` contains:
- `indexed_plugins` - Plugins with downloaded source code
- `available_plugins` - All plugins from PluginHub (for downloading)

## Workflow

1. **Find relevant plugins**: Use `list_plugins.py --search` to find plugins with features you want to learn from
2. **Download sources**: Use `download_plugin_source.py` to get the source code
3. **Index**: Run `index_plugins.py` to build the search index
4. **Search**: Use `search_plugins.py` to find code patterns

## When to Search

Search plugin code when:
- Looking for examples of Harmony patching techniques
- Understanding how other plugins implement specific features
- Finding examples of game API usage in plugin context
- Learning plugin development patterns
