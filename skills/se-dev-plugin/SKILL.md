---
name: se-dev-plugin
description: Plugin development for Space Engineers version 1. Search plugin code from PluginHub for examples and patterns.
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*Clean.bat*), Bash(*run_prepare.sh*), Bash(*dotnet build*), Bash(*dotnet clean*), Bash(*uv run search_plugins.py *), Bash(*uv run index_plugins.py*), Bash(*uv run list_plugins.py*), Bash(*uv run download_plugin_source.py *), Bash(*uv run download_pluginhub.py*), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Plugin Skill

Plugin development for Space Engineers version 1.

**⚠️ CRITICAL: Commands run in a UNIX shell (busybox), NOT Windows CMD. Use bash syntax!**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - This will NOT work

**Actions:**

- **prepare**: Run the one-time preparation (Prepare.bat)
- **bash**: Run UNIX shell commands via busybox
- **search**: Search plugin code using `search_plugins.py`

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-plugin` | Show this help |
| 2 | Prepare keywords | `se-dev-plugin prepare`, `se-dev-plugin setup`, `se-dev-plugin init` | prepare |
| 3 | Bash/shell keywords | `se-dev-plugin bash`, `se-dev-plugin grep`, `se-dev-plugin cat` | bash |
| 4 | Search keywords | `se-dev-plugin search`, `se-dev-plugin find class`, `se-dev-plugin lookup` | search |

## Getting Started

**⚠️ CRITICAL: Before running ANY commands, read [CommandExecution.md](CommandExecution.md) to avoid common mistakes that cause command failures.**

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps first. See the [prepare action](./actions/prepare.md).

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - How to run commands correctly on Windows

## Plugin Development Documentation

Read the appropriate documents for further details:
- [Plugin.md](Plugin.md) Plugin development (shared skills for both client and server)
- [ClientPlugin.md](ClientPlugin.md) Client plugin development (relevant on client side)
- [ServerPlugin.md](ServerPlugin.md) Server plugin development (relevant on server side)
- [Guide.md](Guide.md) Use this to answer questions about the plugin development process in general.
- [Publicizer.md](Publicizer.md) How to use the Krafs publicizer to access internal, protected or private members in the original game code (optional).
- [OtherPluginsAsExamples.md](OtherPluginsAsExamples.md) How to look into the source code of other plugins as examples.

## Harmony Patching Documentation

Progressive documentation for Harmony patching (start with basics, then read advanced topics as needed):

1. **[Patching.md](Patching.md)** - Start here: patch types, prefix/postfix basics, common patterns
2. **[PatchInjections.md](PatchInjections.md)** - Special parameters: `__instance`, `__result`, `___fields`, `__state`
3. **[AccessTools.md](AccessTools.md)** - Reflection utilities for finding methods, fields, and types
4. **[TranspilerPatching.md](TranspilerPatching.md)** - IL-level patching for complex modifications
5. **[PatchingSpecialCases.md](PatchingSpecialCases.md)** - Finalizers, reverse patches, auxiliary methods, priority
6. **[PreloaderPatching.md](PreloaderPatching.md)** - Pre-JIT patching (Mono.Cecil, client only)

## Plugin Distribution

Plugins are released exclusively on the PluginHub. All plugins must be open source, since they are compiled on
the player's machine from the GitHub source revision identified by its PluginHub registration. Plugins are
reviewed for safety and security on submission, but only on a best effort basis, without any legal guarantees.
Plugins are running native code and can do anything.

Use the `se-dev-game-code` skill to search the game's decompiled code. You will need this to
understand how the game's internals work and how to interface with it and patch it properly.

## References

- [Pulsar](https://github.com/SpaceGT/Pulsar) Plugin loader for Space Engineers
- [Pulsar Installer](https://github.com/StarCpt/Pulsar-Installer) Installer for Pulsar on Windows
- [PluginHub](https://github.com/StarCpt/PluginHub/) Public plugin registry for Pulsar

## Plugin Code Search

Search the source code of plugins from PluginHub for examples and patterns:

```bash
# List available plugins
uv run list_plugins.py
uv run list_plugins.py --search "camera"

# Download a plugin's source code (use EXACT name from list)
uv run download_plugin_source.py "Tool Switcher"

# Index downloaded plugins (automatic after download)
uv run index_plugins.py

# Search plugin code
uv run search_plugins.py class declaration Plugin
uv run search_plugins.py method signature Patch

# Count results before viewing (useful for large result sets)
uv run search_plugins.py class usage Plugin --count

# Limit number of results
uv run search_plugins.py class usage IPlugin --limit 20
```

The PluginHub contains descriptions of all available plugins. Download sources for plugins
that may help with your task, then index and search them.

See [search action](./actions/search.md) for complete documentation.

## Action References

Follow the detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
- [search action](./actions/search.md) - Search plugin code for examples

## Remarks

The original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
