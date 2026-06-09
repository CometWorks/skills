# Command Execution Guide

> **CRITICAL: Read this before running any commands in this skill.**

This guide explains how to correctly execute commands on Windows when using this skill. Following these rules prevents command failures and retries.

## ⚡ Quick Start (Read This First!)

**For 99% of use cases, follow these steps:**

1. **Check if prepared:** Look for `Prepare.DONE` file in skill folder
2. **If not prepared, run preparation:**
   ```bash
   ./Prepare.bat (with workdir set to where this documentation files is located)
   ```
3. **Search mod code:**
   ```bash
   uv run search_mods.py class declaration SessionComponent
   uv run search_mods.py method usage Update
   ```
   (Always use workdir parameter set to skill folder)

**That's it!** For issues or more detail, see [Detailed Command Execution Guide](CommandExecutionDetails.md).
