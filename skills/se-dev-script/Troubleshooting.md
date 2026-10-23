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

4. **Searching for PB API names (game types, `Echo`, `GridTerminalSystem`, ...)**:
   - Scripts don't declare them, they use them through the PB API
   - Search for usages, not declarations, under the `field` category (see [How usages are indexed](#how-usages-are-indexed)):
   ```bash
   # Won't find anything (scripts don't declare it)
   uv run search_scripts.py class declaration IMyTerminalBlock

   # Find how scripts use it
   uv run search_scripts.py field usage IMyTerminalBlock
   ```

5. **Name used only after a dot** (`GridTerminalSystem.GetBlocksOfType(...)`, `UpdateFrequency.Update10`):
   not in the index, grep the script sources (see [How usages are indexed](#how-usages-are-indexed)).

### How usages are indexed

- A `usage` row in `class`, `interface`, `struct`, `enum`, `method`, `property`, `event` or `constructor`
  is recorded only for names the indexed scripts declare themselves (for example `class usage Program`).
- Every other identifier, including all PB API names, is recorded as a `field` usage.
  Search `IMyThrust`, `IMyTextSurface`, `Echo`, `Storage`, `argument` with `field usage`.
- Identifiers in a member access (`GridTerminalSystem.GetBlocksOfType`, `Runtime.UpdateFrequency`,
  `UpdateFrequency.Update10`) are not indexed at all.
- Usage search (except `method` and `constructor`) currently finds only uses outside method bodies:
  for a use inside a method it compares the method's name, not the used name.
  A count of 0 or 1 does not mean a name is unused.
- Steam Workshop `Script.cs` files hold only the body of the `Program` class. The indexer sees
  their members as top-level statements, so `class declaration Program` and `method declaration Main`
  find only scripts kept as C# projects (with `class Program : MyGridProgram`), mostly local ones.

For a complete list of uses, grep the script sources. Local scripts are under `LocalScripts/`,
each script's folder is the `path` field in `Data/scripts.json`:
```bash
grep -rnw GetBlocksOfType LocalScripts/ | head -20
grep -rlw UpdateFrequency LocalScripts/ "<workshop path from Data/scripts.json>"
```

### Debugging Strategy

```bash
# Step 1: Check the script inventory
cat Data/scripts.json 2>/dev/null || echo "No inventory - run: uv run list_scripts.py"

# Step 2: Count files indexed
wc -l Data/CodeIndex/*.csv 2>/dev/null

# Step 3: Count all indexed identifier uses (any script has some)
uv run search_scripts.py field usage re:. --count

# Step 4: If still nothing, verify scripts exist
uv run list_scripts.py
```

## Too Many Results

When searches return hundreds or thousands of matches:

### 1. Count First
```bash
uv run search_scripts.py field usage IMyTerminalBlock --count
```

### 2. Use Limit to Preview
```bash
# Show first 30 matches
uv run search_scripts.py field usage IMyTerminalBlock --limit 30
```

### 3. Refine Your Search
```bash
# Too broad: substring match, also IMyTerminalAction, IMyTerminalBlockGroup, ...
uv run search_scripts.py field usage IMyTerminal --count

# More specific - use regex (re: prefix), exact name only
uv run search_scripts.py field usage "re:^IMyTerminalBlock$" --limit 20

# Only one script's code: filter by namespace prefix
uv run search_scripts.py field usage "re:^IMyTerminalBlock$" -n IngameScript --limit 20
```

### 4. Paginate Through Results
```bash
uv run search_scripts.py field usage IMyTerminalBlock --limit 10 --offset 0
uv run search_scripts.py field usage IMyTerminalBlock --limit 10 --offset 10
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
- `Program` class (main entry point), implicit in Workshop `Script.cs` files
- `Program()` constructor (runs on compile and world load, restores state from `Storage`)
- `Main()` method (runs on each trigger or update)
- `Save()` method (persistence into `Storage`)

These declarations are found only in scripts kept as C# projects, see [How usages are indexed](#how-usages-are-indexed).

```bash
# Find Program classes
uv run search_scripts.py class declaration Program --limit 10

# Find Main implementations
uv run search_scripts.py method declaration Main --limit 20
```

### 2. Common API Usage

```bash
# Terminal system usage (only after a dot, not indexed: grep)
grep -rnw GridTerminalSystem LocalScripts/ | head -15

# Block interface usage
uv run search_scripts.py field usage IMyThrust --limit 10
uv run search_scripts.py field usage IMyDoor --limit 10

# Display/LCD usage
uv run search_scripts.py field usage IMyTextPanel --limit 15
```

## Search Tips

### 1. Search for Common PB Patterns

```bash
# Find echo output usage (Echo is a PB API property, so field usage)
uv run search_scripts.py field usage "re:^Echo$" --limit 20

# Find GetBlocksOfType usage (called after a dot, not indexed: grep)
grep -rnw GetBlocksOfType LocalScripts/ | head -15

# Find argument parsing
uv run search_scripts.py field usage "re:^argument$" --limit 20
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

Many Workshop scripts were merged from multiple source files by a merge tool (MDK, ScriptMerge),
some also minified with one-letter (often Unicode) names. Hits in minified code are hard to read,
prefer scripts with readable names. One-letter declarations point at minified scripts:
```bash
uv run search_scripts.py class declaration "re:^.$" --limit 5
```

## Common Script Patterns to Search For

```bash
# Find Program class implementations
uv run search_scripts.py class declaration Program --limit 10

# Find UpdateFrequency usage (used after a dot, not indexed: grep)
grep -rnw UpdateFrequency LocalScripts/ | head -15

# Find LCD/display scripts
uv run search_scripts.py field usage IMyTextSurface --limit 20

# Find autopilot/control scripts
uv run search_scripts.py field usage IMyRemoteControl --limit 10

# Find inventory management
uv run search_scripts.py field usage IMyInventory --limit 15
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

4. **Try a broad search** (any indexed identifier use):
   ```bash
   uv run search_scripts.py field usage re:. --limit 5
   ```
