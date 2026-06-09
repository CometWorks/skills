---
name: se-dev-plugin
description: Plugin development for Space Engineers version 1. Search plugin code from PluginHub for examples and patterns.
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*prepare.sh*), Bash(*Clean.bat*), Bash(*dotnet build*), Bash(*dotnet clean*), Bash(*uv run search_plugins.py *), Bash(*uv run index_plugins.py*), Bash(*uv run list_plugins.py*), Bash(*uv run download_plugin_source.py *), Bash(*uv run download_pluginhub.py*), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Plugin Skill

Plugin development for Space Engineers version 1.

**⚠️ CRITICAL: Commands run in UNIX shell. Use bash syntax. On Windows this is BusyBox; on Linux use native shell.**

Examples:
- ✅ `test -f file.txt && echo exists`
- ✅ `ls -la | head -10`
- ❌ `if exist file.txt (echo exists)` - Will NOT work

**Actions:**

- **prepare**: Run one-time preparation (`Prepare.bat` on Windows, `prepare.sh` on Linux)
- **bash**: Run UNIX shell commands via busybox
- **search**: Search plugin code using `search_plugins.py`

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-plugin` | Show help |
| 2 | Prepare keywords | `se-dev-plugin prepare`, `se-dev-plugin setup`, `se-dev-plugin init` | prepare |
| 3 | Bash/shell keywords | `se-dev-plugin bash`, `se-dev-plugin grep`, `se-dev-plugin cat` | bash |
| 4 | Search keywords | `se-dev-plugin search`, `se-dev-plugin find class`, `se-dev-plugin lookup` | search |

## Getting Started

**⚠️ CRITICAL: Before running ANY commands, read [CommandExecution.md](CommandExecution.md) to avoid common mistakes that cause command failures.**

If `Prepare.DONE` file missing in this folder, you MUST run one-time preparation steps first. See [prepare action](./actions/prepare.md).

## Essential Documentation

- **[CommandExecution.md](CommandExecution.md)** - ⚠️ **READ THIS FIRST** - Windows command execution details; on Linux keep bash syntax and use `prepare.sh`

## Plugin Development Documentation

Read appropriate documents for further details:
- [Plugin.md](Plugin.md) Plugin development (shared skills for both client and server)
- [ClientPlugin.md](ClientPlugin.md) Client plugin development (relevant on client side)
- [ServerPlugin.md](ServerPlugin.md) Server plugin development (relevant on server side)
- [Guide.md](Guide.md) Use this to answer questions about plugin development process in general.
- [Publicizer.md](Publicizer.md) How to use Krafs publicizer to access internal, protected or private members in original game code (optional).
- [OtherPluginsAsExamples.md](OtherPluginsAsExamples.md) How to look into source code of other plugins as examples.

## Harmony Patching Documentation

Progressive documentation for Harmony patching (start with basics, then read advanced topics as needed):

1. **[Patching.md](Patching.md)** - Start here: patch types, prefix/postfix basics, common patterns
2. **[PatchInjections.md](PatchInjections.md)** - Special parameters: `__instance`, `__result`, `___fields`, `__state`
3. **[AccessTools.md](AccessTools.md)** - Reflection utilities to find methods, fields, and types
4. **[TranspilerPatching.md](TranspilerPatching.md)** - IL-level patching for complex modifications
5. **[PatchingSpecialCases.md](PatchingSpecialCases.md)** - Finalizers, reverse patches, auxiliary methods, priority
6. **[PreloaderPatching.md](PreloaderPatching.md)** - Pre-JIT patching (Mono.Cecil, client only)

## Targets: Client and Server

Plugins target one or both of:
- **Client** — runs inside game client, loaded by [Pulsar](https://github.com/SpaceGT/Pulsar), released on [PluginHub](https://github.com/StarCpt/PluginHub/).
- **Server** — runs inside dedicated server, loaded by [Magnetar](https://magnetar.se), released on [MagnetarHub](https://github.com/viktor-ferenczi/MagnetarHub). Server plugins declare their configuration through Magnetar's PluginSdk; use **`se-dev-plugin-sdk`** skill for that. Admins configure server plugins remotely via [Quasar](https://github.com/viktor-ferenczi/Quasar), the Magnetar control plane.

A client-only plugin uses [client plugin template](https://github.com/viktor-ferenczi/se-client-plugin-template). A plugin that also needs server side companion (or is server-only) uses [server plugin template](https://github.com/viktor-ferenczi/se-server-plugin-template), which has `ClientPlugin` target, `ServerPlugin` target and `Shared` project. See [ServerPlugin.md](ServerPlugin.md).

## Plugin Distribution

Client plugins released exclusively on PluginHub. All client plugins must be open source, since they are compiled on
player's machine from GitHub source revision identified by its PluginHub registration. Plugins are
reviewed for safety and security on submission, but only on best effort basis, without any legal guarantees.
Plugins run native code and can do anything.

Use `se-dev-game-code` skill to search game's decompiled code. Need this to
understand how game's internals work and how to interface with it and patch it properly.

## References

- [Pulsar](https://github.com/SpaceGT/Pulsar) Plugin loader for Space Engineers game client
- [Pulsar Installer](https://github.com/StarCpt/Pulsar-Installer) Installer for Pulsar on Windows
- [PluginHub](https://github.com/StarCpt/PluginHub/) Public plugin registry for Pulsar
- [Magnetar](https://magnetar.se) Plugin loader for Space Engineers dedicated server
- [MagnetarHub](https://github.com/viktor-ferenczi/MagnetarHub) Public plugin registry for Magnetar

## Plugin Code Search

Search source code of plugins from PluginHub for examples and patterns:

```bash
# List available plugins
uv run list_plugins.py
uv run list_plugins.py --search "camera"

# Download plugin's source code (use EXACT name from list)
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

PluginHub contains descriptions of all available plugins. Download sources for plugins
that may help with your task, then index and search them.

See [search action](./actions/search.md) for complete documentation.

## Action References

Follow detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Run UNIX shell commands via busybox
- [search action](./actions/search.md) - Search plugin code for examples

## Remarks

Original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
