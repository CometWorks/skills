---
name: se-dev-torch
description: Torch plugin development for Space Engineers version 1. Search TorchAPI/Torch source code, plugin API, managers, commands, and server UI patterns.
license: MIT
allowed-tools: Read, Bash(*Prepare.bat*), Bash(*Prepare.sh*), Bash(*Clean.bat*), Bash(*run_prepare.sh*), Bash(*uv run search_torch.py *), Bash(*uv run index_torch.py *), Bash(*busybox* grep *), Bash(*busybox* find *), Bash(*busybox* cat *), Bash(*busybox* head *), Bash(*busybox* tail *), Bash(*busybox* ls*), Bash(*busybox* wc *), Bash(*busybox* sort *), Bash(*busybox* uniq *), Bash(*busybox* tree*)
---

# SE Dev Torch Skill

Torch plugin development for Space Engineers version 1.

This skill is for Torch framework itself: plugin lifecycle, manifests, commands, managers, patch helpers, and server UI integration. Use `se-dev-game-code` or `se-dev-server-code` alongside it when task crosses into Keen internals.

**Compatibility:** Plugins built with this skill target **Torch only** — **not** compatible with [Magnetar](https://magnetar.se), which uses different patcher and SDK. For Magnetar server plugins use `se-dev-plugin` and `se-dev-plugin-sdk` skills. When starting from [se-server-plugin-template](https://github.com/CometWorks/server-plugin-template), use its **`last-torch-compatible`** tag as basis, not current `main` (which dropped Torch target). See [TorchPlugin.md](TorchPlugin.md).

**CRITICAL: Commands run in a UNIX shell. Use bash syntax. On Windows this is BusyBox; on Linux/macOS use the native shell.**

Examples:
- `test -f Prepare.DONE && echo ready`
- `TORCH_ROOT=/path/to/Torch ./Prepare.sh`
- `if exist Prepare.DONE echo ready`

**Actions:**

- **prepare**: Run one-time preparation (`Prepare.bat` on Windows, `Prepare.sh` on Linux/macOS, or `run_prepare.sh` as wrapper)
- **bash**: Run UNIX shell commands via busybox
- **search**: Search indexed Torch source using `search_torch.py`

## Routing Decision

Check these patterns in order:

| Priority | Pattern | Example | Route |
|----------|---------|---------|-------|
| 1 | Empty or bare invocation | `se-dev-torch` | Show this help |
| 2 | Prepare keywords | `se-dev-torch prepare`, `se-dev-torch setup`, `se-dev-torch init` | prepare |
| 3 | Bash/shell keywords | `se-dev-torch bash`, `se-dev-torch grep`, `se-dev-torch cat` | bash |
| 4 | Search keywords | `se-dev-torch search`, `se-dev-torch find class`, `se-dev-torch lookup` | search |

## Requirements

Host system must have following on `PATH`:

- **Python** 3.11 or newer
- **git** command line client

If user already has local Torch checkout, set `TORCH_ROOT` to that repository root before preparation. Otherwise skill clones `https://github.com/TorchAPI/Torch` into its persistent data folder.

## Getting Started

**CRITICAL: Before running ANY commands, read [CommandExecution.md](CommandExecution.md).**

If `Prepare.DONE` file missing in this folder, run one-time preparation first. See [Prepare.md](Prepare.md).

## Essential Documentation

- [CommandExecution.md](CommandExecution.md) - command execution rules and quick start
- [QuickStart.md](QuickStart.md) - first searches and common task entry points
- [TorchPlugin.md](TorchPlugin.md) - Torch plugin authoring patterns
- [Architecture.md](Architecture.md) - where to inspect each subsystem in Torch source tree
- [CodeSearch.md](CodeSearch.md) - complete code search reference
- [Troubleshooting.md](Troubleshooting.md) - common failure modes and what to check

## Quick Search Examples

```bash
# Find the base plugin class
uv run search_torch.py class declaration TorchPluginBase

# Find the Torch plugin API interfaces
uv run search_torch.py interface declaration ITorchPlugin -n Torch.API.Plugins

# Inspect command definitions
uv run search_torch.py class declaration CommandModule -n Torch.Commands
uv run search_torch.py method signature RegisterPluginCommands

# Inspect manager usage patterns
uv run search_torch.py class declaration DependencyManager -n Torch.Managers
uv run search_torch.py interface declaration ITorchSessionManager -n Torch.API.Session

# Find patching infrastructure
uv run search_torch.py namespace declaration PatchManager
uv run search_torch.py class declaration PatchContext -n Torch.Managers.PatchManager
```

## General Rules

- Search only indexed Torch repository selected during preparation.
- Prefer `manifest.xml` metadata over `[PluginAttribute]`; `PluginAttribute` is obsolete in Torch.
- Prefer `torch.Managers.GetManager<T>()` or `session.Managers.GetManager<T>()` over obsolete `ITorchBase.GetManager<T>()`.
- Use `TorchPluginBase` as normal starting point unless task clearly needs lower-level implementation.
- If task is about Space Engineers game behavior rather than Torch framework behavior, use `se-dev-game-code` or `se-dev-server-code` as companion skill.

## Remarks

Original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
