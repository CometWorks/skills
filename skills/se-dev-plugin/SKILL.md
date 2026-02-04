---
name: se-dev-plugin
description: Plugin development for Space Engineers version 1
argument-hint: prepare | bash
license: MIT
---

# SE Dev Plugin Skill

Plugin development for Space Engineers version 1.

**Actions:**

- **prepare**: Run the one-time preparation (Prepare.bat)
- **bash**: Run UNIX shell commands via busybox

## Routing Decision

Check these patterns **in order** - first match wins:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-plugin` | Show this help |
| 2 | Prepare keywords | `se-dev-plugin prepare`, `se-dev-plugin setup`, `se-dev-plugin init` | prepare |
| 3 | Bash/shell keywords | `se-dev-plugin bash`, `se-dev-plugin grep`, `se-dev-plugin find` | bash |

## Getting Started

If the `Prepare.DONE` file is missing in this folder, you MUST run the one-time preparation steps first. See the [prepare action](./actions/prepare.md).

## Plugin Development Documentation

Read the appropriate documents for further details:
- [Plugin.md](Plugin.md) Plugin development (shared skills for both client and server)
- [ClientPlugin.md](ClientPlugin.md) Client plugin development (relevant on client side)
- [ServerPlugin.md](ServerPlugin.md) Server plugin development (relevant on server side)
- [Guide.md](Guide.md) Use this to answer questions about the plugin development process in general.
- [Publicizer.md](Publicizer.md) How to use the Krafs publicizer to access internal, protected or private members in the original game code (optional).
- [OtherPluginsAsExamples.md](OtherPluginsAsExamples.md) How to look into the source code of other plugins as examples.

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

## Action References

Follow the detailed instructions in:

- [prepare action](./actions/prepare.md) - One-time preparation
- [bash action](./actions/bash.md) - Running UNIX shell commands via busybox
