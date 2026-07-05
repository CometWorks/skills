# Troubleshooting Guide

Resolve common issues when searching mod code.

## NO-MATCHES Results

### Common Causes

1. **Wrong skill**:
   - Game classes like `MyCubeBlock` → use `se-dev-game-code`
   - Mod code examples → use `se-dev-mod` ✅
   - Plugin code → use `se-dev-plugin`
   - Script code → use `se-dev-script`

2. **No mods installed or indexed**:
   ```bash
   # List the mods the skill can see (steam + local)
   uv run list_mods.py

   # Check if the code index exists
   test -d Data/CodeIndex && echo "Index exists" || echo "Need to index"
   ```

3. **Index not built**:
   ```bash
   # Build/rebuild the index
   uv run index_mods.py
   ```

4. **Searching for base game classes**:
   - Mods don't typically *declare* game classes like `MyGameLogicComponent`
   - They *use* them instead
   - Search for usages, not declarations:
   ```bash
   # Likely won't find anything (mods don't declare it)
   uv run search_mods.py class declaration MyGameLogicComponent

   # Finds how mods use it
   uv run search_mods.py class usage MyGameLogicComponent
   ```

### Debugging Strategy

```bash
# Step 1: Check the mod inventory
cat Data/mods.json 2>/dev/null || echo "No inventory - run: uv run list_mods.py"

# Step 2: Count files indexed
wc -l Data/CodeIndex/*.csv 2>/dev/null

# Step 3: Try a common search
uv run search_mods.py class usage Init --count

# Step 4: If still nothing, verify mods exist
uv run list_mods.py
```

## Too Many Results

When searches return hundreds or thousands of matches:

### 1. Count First
```bash
uv run search_mods.py class usage Init --count
```

### 2. Use Limit to Preview
```bash
# Show first 20 matches
uv run search_mods.py class usage Init --limit 20
```

### 3. Refine Your Search
```bash
# Too broad
uv run search_mods.py method usage Update --count

# More specific with namespace
uv run search_mods.py method usage Update -n YourModNamespace
```

### 4. Paginate Through Results
```bash
uv run search_mods.py class usage Init --limit 10 --offset 0
uv run search_mods.py class usage Init --limit 10 --offset 20
```

## Index Issues

### Re-indexing After Subscribing to New Mods

**IMPORTANT**: Game must download mods before they can be indexed.

```bash
# 1. Subscribe to mods on Steam Workshop
# 2. Start game and load a world (downloads mods)
# 3. Exit game
# 4. Re-index (incremental: only changed mods are reparsed)
uv run index_mods.py
```

### Checking What's Indexed

```bash
# See indexed mods
cat Data/mods.json

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
uv run index_mods.py
```

## Finding the Right Mods

If looking for specific functionality:

### 1. Search Mod Code for a Feature
```bash
# Find mods that use a thruster interface
uv run search_mods.py class usage IMyThrust --limit 10
```

### 2. Browse the Mod Inventory
```bash
# List every mod the skill can see, with source and path
uv run list_mods.py
```

### 3. Check Local Development Mods
```bash
# Your own mods in development (symlink to the game's local-mod folder)
ls LocalMods/
```

## Search Tips

### 1. Search for Patterns Mods Actually Use

Common patterns in mods:
```bash
# Session components
uv run search_mods.py class children MySessionComponentBase

# Block game logic
uv run search_mods.py class children MyGameLogicComponent

# Common method names
uv run search_mods.py method usage Init
uv run search_mods.py method usage UpdateBeforeSimulation
uv run search_mods.py method usage UpdateAfterSimulation
```

### 2. Remember the Mod API Whitelist

Mods can only use names from `ModApiWhitelist.txt`. If searching for something not on whitelist, you won't find it in mods.

```bash
# Check if name whitelisted
grep "MyCubeBlock" ModApiWhitelist.txt
```

### 3. Use se-dev-game-code for Base Classes

To understand what you can inherit from or how classes work:
```bash
# Wrong skill - won't find definition
uv run search_mods.py class declaration MyGameLogicComponent

# Right skill - finds actual definition
# (switch to se-dev-game-code skill)
uv run search_game_code.py class declaration MyGameLogicComponent
```

## Common Mod Patterns to Search For

```bash
# Find session components
uv run search_mods.py class children MySessionComponentBase --limit 10

# Find block logic implementations
uv run search_mods.py class usage MyGameLogicComponent --limit 20

# Find network message handling
uv run search_mods.py method usage RegisterMessageHandler --limit 10

# Find definition changes
uv run search_mods.py class usage MyCubeBlockDefinition --limit 15
```

## Still Having Issues?

1. **Verify mods exist**:
   ```bash
   uv run list_mods.py
   ```

2. **Check preparation completed**:
   ```bash
   test -f Prepare.DONE && echo "OK" || echo "Run Prepare.bat (Windows) or ./prepare.sh (Linux)"
   ```

3. **Verify index exists**:
   ```bash
   test -d Data/CodeIndex && echo "OK" || echo "Run: uv run index_mods.py"
   ```

4. **Try a broad usage search**:
   ```bash
   uv run search_mods.py class usage Init --limit 5
   ```
