# Command Execution Guide

> **CRITICAL: Read this before running any commands in this skill.**

This guide explains how to execute commands correctly for Torch skill.

## Quick Start

For most use cases, follow these steps:

1. **Check if prepared:** Look for `Prepare.DONE` file in skill folder
2. **If not prepared, run preparation:**
   ```bash
   TORCH_ROOT=/path/to/Torch ./Prepare.sh
   ```
   If `TORCH_ROOT` not set, preparation clones `TorchAPI/Torch` automatically.
3. **Inspect plugin entry points:**
   ```bash
   uv run search_torch.py class declaration TorchPluginBase
   uv run search_torch.py interface declaration ITorchPlugin -n Torch.API.Plugins
   ```
4. **Search Torch source:**
   ```bash
   uv run search_torch.py class declaration PluginManager -n Torch.Managers
   uv run search_torch.py method signature RegisterPluginCommands
   ```
   (Always use workdir parameter set to skill folder)

Need more detail? Read [CommandExecutionDetails.md](CommandExecutionDetails.md).
