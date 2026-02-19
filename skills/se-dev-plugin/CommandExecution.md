# Command Execution Guide

> **CRITICAL: Read this before running any commands in this skill.**

This guide explains how to correctly execute commands on Windows when using this skill. Following these rules will prevent command failures and retries.

## ⚡ Quick Start (Read This First!)

**For 99% of use cases, follow these simple steps:**

1. **Check if prepared:** Look for `Prepare.DONE` file in skill folder
2. **If not prepared, run preparation:**
   ```bash
   ./Prepare.bat (with workdir set to where this documentation files is located)
   ```
3. **List and download plugins:**
   ```bash
   uv run list_plugins.py
   uv run download_plugin_source.py "Plugin Name"
   ```
4. **Search plugin code:**
   ```bash
   uv run search_plugins.py class declaration Plugin
   uv run search_plugins.py method usage Patch
   ```
   (Always use workdir parameter set to the skill folder)

**That's it!** If you encounter issues or need more detailed information, see the [Detailed Command Execution Guide](CommandExecutionDetails.md).
