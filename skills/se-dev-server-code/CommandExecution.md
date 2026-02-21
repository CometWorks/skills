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
3. **Search server code:**
   ```bash
   # Correct syntax: <category> <type> <pattern>
   uv run search_code.py class declaration MyCubeGrid
   uv run search_code.py method usage GetPosition
   uv run search_code.py interface declaration IMyTerminalBlock
   ```
   (Always use workdir parameter set to the skill folder)

**That's it!** If you encounter issues or need more detailed information, see the [Detailed Command Execution Guide](CommandExecutionDetails.md).
