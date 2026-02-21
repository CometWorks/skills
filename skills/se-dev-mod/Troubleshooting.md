# Troubleshooting Guide

This guide helps you resolve common issues when searching mod code.

## NO-MATCHES Results

### Common Causes

1. **Wrong skill**: 
   - Game classes like `MyCubeBlock` → use `se-dev-game-code`
   - Mod code examples → use `se-dev-mod` ✅
   - Plugin code → use `se-dev-plugin`
   - Script code → use `se-dev-script`

2. **No mods subscribed or indexed**:
   ```bash
   # Check if you have any mods
   ls SteamMods/ | head -5
   ls LocalMods/ | head -5
   
   # Check if index exists
   test -d ModCodeIndex && echo "Index exists" || echo "Need to index"
   ```

3. **Index not built**:
   ```bash
   # Build/rebuild the index
   uv run index_mods.py
   ```

4. **Searching for base game classes**: 
   - Mods don't typically *declare* game classes like `MyGameLogicComponent`
   - They *use* them instead
   - Try searching for usages, not declarations:
   ```bash
   # This likely won't find anything (mods don't declare it)
   uv run search_mods.py class declaration MyGameLogicComponent
   
   # This will find how mods use it
   uv run search_mods.py class usage MyGameLogicComponent
   ```

### Debugging Strategy

```bash
# Step 1: Check if any mods are indexed
cat ModCodeIndex/plugins.json 2>/dev/null || echo "No index"

# Step 2: Count files indexed
wc -l ModCodeIndex/*.csv 2>/dev/null

# Step 3: Try a very common search
uv run search_mods.py class usage Init --count

# Step 4: If still nothing, verify mods exist
ls SteamMods/ | wc -l
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

**IMPORTANT**: The game must download mods before they can be indexed.

```bash
# 1. Subscribe to mods on Steam Workshop
# 2. Start the game and load a world (this downloads the mods)
# 3. Exit the game
# 4. Re-index
uv run index_mods.py
```

### Checking What's Indexed

```bash
# See indexed mods
cat ModCodeIndex/plugins.json

# Count mod files
find SteamMods/ -name "*.cs" | wc -l
find LocalMods/ -name "*.cs" | wc -l

# Check index size
ls -lh ModCodeIndex/
```

### Rebuilding Index

```bash
# Delete old index
rm -rf ModCodeIndex/

# Rebuild
uv run index_mods.py
```

## Finding the Right Mods

If you're looking for specific functionality:

### 1. Search Mod Files Directly
```bash
# Find mods that mention "thruster"
grep -r "thruster" SteamMods/*/Data/Scripts/ | cut -d: -f1 | sort -u | head -10
```

### 2. Look at Mod Names
```bash
# Browse mod directories
ls -d SteamMods/*/ | head -20
```

### 3. Check Local Development Mods
```bash
# Your own mods in development
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

Mods can only use names from `ModApiWhitelist.txt`. If searching for something not on the whitelist, you won't find it in mods.

```bash
# Check if name is whitelisted
grep "MyCubeBlock" ModApiWhitelist.txt
```

### 3. Use se-dev-game-code for Base Classes

To understand what you can inherit from or how classes work:
```bash
# Wrong skill - won't find definition
uv run search_mods.py class declaration MyGameLogicComponent

# Right skill - find the actual definition
# (switch to se-dev-game-code skill)
uv run search_code.py class declaration MyGameLogicComponent
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
   ls SteamMods/ | wc -l
   ls LocalMods/ | wc -l
   ```

2. **Check preparation completed**:
   ```bash
   test -f Prepare.DONE && echo "OK" || echo "Run ./Prepare.bat"
   ```

3. **Verify index exists**:
   ```bash
   test -d ModCodeIndex && echo "OK" || echo "Run: uv run index_mods.py"
   ```

4. **Try fallback search**:
   ```bash
   grep -r "class.*Init" SteamMods/*/Data/Scripts/*.cs | head -5
   ```
