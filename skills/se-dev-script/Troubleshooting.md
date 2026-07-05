# Troubleshooting Guide

This guide helps resolve common issues when searching script code.

## NO-MATCHES Results

### Common Causes

1. **Wrong skill**:
   - Game classes like `MyCubeBlock` → use `se-dev-game-code`
   - Mod code examples → use `se-dev-mod`
   - Plugin code → use `se-dev-plugin`
   - PB script examples → use `se-dev-script` ✅

2. **No scripts installed or indexed**:
   ```bash
   # List the scripts the skill can see (steam + local)
   uv run list_scripts.py

   # Check if the code index exists
   test -d Data/CodeIndex && echo "Index exists" || echo "Need to index"
   ```

3. **Index not built**:
   ```bash
   # Build/rebuild index
   uv run index_scripts.py
   ```

4. **Searching for base game classes**:
   - Scripts don't declare game classes
   - They use them through the PB API
   - Search for usages, not declarations:
   ```bash
   # Won't find anything (scripts don't declare it)
   uv run search_scripts.py class declaration IMyTerminalBlock

   # Find how scripts use it
   uv run search_scripts.py class usage IMyTerminalBlock
   ```

### Debugging Strategy

```bash
# Step 1: Check the script inventory
cat Data/scripts.json 2>/dev/null || echo "No inventory - run: uv run list_scripts.py"

# Step 2: Count files indexed
wc -l Data/CodeIndex/*.csv 2>/dev/null

# Step 3: Try searching for "Program" (every script has this)
uv run search_scripts.py class declaration Program --count

# Step 4: If still nothing, verify scripts exist
uv run list_scripts.py
```

## Too Many Results

When searches return hundreds or thousands of matches:

### 1. Count First
```bash
uv run search_scripts.py class usage GridTerminalSystem --count
```

### 2. Use Limit to Preview
```bash
# Show first 30 matches
uv run search_scripts.py class usage GridTerminalSystem --limit 30
```

### 3. Refine Your Search
```bash
# Too broad
uv run search_scripts.py method usage Main --count

# More specific - use regex
uv run search_scripts.py method usage "Main.*void" --limit 20
```

### 4. Paginate Through Results
```bash
uv run search_scripts.py class usage Program --limit 10 --offset 0
uv run search_scripts.py class usage Program --limit 10 --offset 20
```

## Index Issues

### Re-indexing After Subscribing to New Scripts

**IMPORTANT**: Game must download scripts before they can be indexed.

```bash
# 1. Subscribe to scripts on Steam Workshop
# 2. Start game, open PB, browse script list (downloads them)
# 3. Exit game
# 4. Re-index (incremental: only changed scripts are reparsed)
uv run index_scripts.py
```

### Checking What's Indexed

```bash
# See indexed scripts
cat Data/scripts.json

# Count indexed symbols per category
wc -l Data/CodeIndex/*.csv

# Check index size
ls -lh Data/CodeIndex/
```

### Rebuilding Index

```bash
# Delete old index
rm -rf Data/CodeIndex/

# Rebuild
uv run index_scripts.py
```

## Finding the Right Scripts

### 1. Script Structure

PB scripts typically have:
- `Program` class (main entry point)
- `Main()` method (called each tick)
- `Save()` and `Load()` methods (persistence)

```bash
# Find Program classes
uv run search_scripts.py class declaration Program --limit 10

# Find Main implementations
uv run search_scripts.py method declaration Main --limit 20
```

### 2. Common API Usage

```bash
# Terminal system usage
uv run search_scripts.py class usage GridTerminalSystem --limit 15

# Block interface usage
uv run search_scripts.py class usage IMyThrust --limit 10
uv run search_scripts.py class usage IMyDoor --limit 10

# Display/LCD usage
uv run search_scripts.py class usage IMyTextPanel --limit 15
```

## Search Tips

### 1. Search for Common PB Patterns

```bash
# Find echo output usage
uv run search_scripts.py method usage Echo --limit 20

# Find GetBlocksOfType usage
uv run search_scripts.py method usage GetBlocksOfType --limit 15

# Find argument parsing
uv run search_scripts.py field usage argument --limit 20
```

### 2. Remember the PB API Whitelist

Scripts can only use names from `PBApiWhitelist.txt`.

```bash
# Check if name available to PB scripts
grep "IMyThrust" PBApiWhitelist.txt
```

### 3. Use se-dev-game-code for Base Classes

To understand interfaces and base classes:
```bash
# Wrong skill - won't find definition
uv run search_scripts.py interface declaration IMyTerminalBlock

# Right skill - find actual definition
# (switch to se-dev-game-code skill)
uv run search_game_code.py interface declaration IMyTerminalBlock
```

### 4. Look for Merged Scripts

Many scripts merged from multiple files. Look for comments like:
```bash
uv run search_scripts.py class usage Program --limit 5
```

## Common Script Patterns to Search For

```bash
# Find Program class implementations
uv run search_scripts.py class declaration Program --limit 10

# Find UpdateFrequency usage
uv run search_scripts.py field usage UpdateFrequency --limit 15

# Find LCD/display scripts
uv run search_scripts.py class usage IMyTextSurface --limit 20

# Find autopilot/control scripts
uv run search_scripts.py class usage IMyRemoteControl --limit 10

# Find inventory management
uv run search_scripts.py class usage IMyInventory --limit 15
```

## Still Having Issues?

1. **Verify scripts exist**:
   ```bash
   uv run list_scripts.py
   ```

2. **Check preparation completed**:
   ```bash
   test -f Prepare.DONE && echo "OK" || echo "Run Prepare.bat (Windows) or ./prepare.sh (Linux)"
   ```

3. **Verify index exists**:
   ```bash
   test -d Data/CodeIndex && echo "OK" || echo "Run: uv run index_scripts.py"
   ```

4. **Try a broad declaration search**:
   ```bash
   uv run search_scripts.py class declaration Program --limit 5
   ```
