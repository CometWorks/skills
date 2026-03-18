# Advanced Code Search Techniques

Power user techniques for efficient code exploration.

## Complex Regex Patterns

### Exact Name Matching

Avoid partial matches by anchoring patterns:

```bash
# Wrong: matches Vector3D, Vector3DI, Vector3D_Extensions
uv run search_code.py struct declaration Vector3D

# Right: matches only Vector3D
uv run search_code.py struct declaration "re:^Vector3D$"
```

### Pattern Alternatives

```bash
# Match Vector2D OR Vector3D
uv run search_code.py struct declaration "re:^Vector[23]D$"

# Match methods starting with Get or Set
uv run search_code.py method declaration "re:^(Get|Set)"

# Match any My*Block class
uv run search_code.py class declaration "re:^My.*Block$"
```

### Common Patterns

```bash
# All properties (typically PascalCase, no underscores)
uv run search_code.py field declaration "re:^[A-Z][a-zA-Z0-9]*$"

# Private fields (typically start with m_ or _)
uv run search_code.py field declaration "re:^[m_]"

# Interface names (start with I)
uv run search_code.py interface declaration "re:^I[A-Z]"

# Event handlers (typically On* methods)
uv run search_code.py method declaration "re:^On[A-Z]"
```

## Efficient Large Result Workflows

### Count-First Strategy

Always count before fetching large result sets:

```bash
# Step 1: Count
uv run search_code.py -c class usage MyEntity
# Output: 1247

# Step 2: Decide on pagination
# At 10-20 results per query: 1247 / 20 = ~62 queries needed

# Step 3: Sample strategically
uv run search_code.py -l 10 class usage MyEntity           # First 10
uv run search_code.py -l 10 -o 100 class usage MyEntity    # Mid-range sample
uv run search_code.py -l 10 -o 1200 class usage MyEntity   # End sample
```

### Progressive Refinement

Narrow down searches incrementally:

```bash
# Start broad
uv run search_code.py -c -n Sandbox class declaration ""
# Output: 3421

# Narrow to subnamespace
uv run search_code.py -c -n Sandbox.Game class declaration ""
# Output: 1856

# Further narrow
uv run search_code.py -c -n Sandbox.Game.Entities class declaration ""
# Output: 247

# Now fetch results
uv run search_code.py -l 20 -n Sandbox.Game.Entities class declaration ""
```

### Namespace-First Approach

When exploring unfamiliar areas:

```bash
# 1. List all classes in namespace
uv run search_code.py -n VRageMath class declaration ""

# 2. Pick interesting class, find its methods
uv run search_code.py -n VRageMath method declaration "" | grep Vector3D

# 3. Find specific method details
uv run search_code.py -n VRageMath method signature Normalize
```

## Combining Multiple Searches

### Finding Related Code

```bash
# 1. Find class declaration
uv run search_code.py class declaration MyTerminalBlock
# Read the file to understand structure

# 2. Find what implements it (if interface)
uv run search_code.py interface implementors IMyTerminalBlock

# 3. Find usages
uv run search_code.py -l 20 class usage MyTerminalBlock

# 4. Find related methods
uv run search_code.py -n Sandbox.Game method declaration Terminal
```

### Understanding Method Calls

```bash
# 1. Find method signature
uv run search_code.py method signature GetPosition
# See parameters and return types

# 2. Find where it's called
uv run search_code.py -l 10 method usage GetPosition
# Read call sites

# 3. Find similar methods
uv run search_code.py method signature "re:^Get.*Position"
```

### Exploring Class Families

```bash
# 1. Find base class
uv run search_code.py class parent MyFunctionalBlock

# 2. Find siblings
uv run search_code.py class children MyTerminalBlock

# 3. Find what they all implement
uv run search_code.py class implements "re:^My.*Block$"
```

## Signature Search Strategies

Signature searches are useful for understanding method overloads and parameter types. For basic usage, see `CodeSearch.md`.

### Advanced Signature Patterns

```bash
# Find overloaded methods by comparing parameter lists
uv run search_code.py -l 20 method signature Build
# Review different overloads of Build methods

# Find methods accepting specific parameter types
uv run search_code.py method signature "re:.*Vector3D.*"
# Matches method names containing "Vector3D" - review signatures for actual parameters

# Combine with namespace filtering for targeted search
uv run search_code.py -n VRageMath method signature ""
# Then filter output for "static" keyword to find static methods

# Find methods with multiple pattern matches
uv run search_code.py method signature Get Position
# Both "Get" AND "Position" in method name - useful for parameter analysis
```

### Analyzing Method Overloads

When exploring overloaded methods, use signature search to understand the variations:

```bash
# Get count of overloads
uv run search_code.py -c method signature Constructor

# Examine all variations
uv run search_code.py method signature Constructor
# Compare parameter types and modifiers across overloads
```

## Multi-Pattern Searches

Use multiple patterns for AND logic:

```bash
# Find methods containing both "Get" and "Position"
uv run search_code.py method declaration Get Position

# Find classes containing "Grid" and "Physics"
uv run search_code.py class declaration Grid Physics

# Order doesn't matter - both patterns must match
uv run search_code.py method declaration Position Get  # Same result
```

## Assembly-Specific Searches

Target specific DLLs by namespace:

```bash
# Math operations (VRage.Math)
uv run search_code.py -n VRageMath method declaration ""

# Game entities (Sandbox.Game)
uv run search_code.py -n Sandbox.Game.Entities class declaration ""

# Object builders (SpaceEngineers.ObjectBuilders)
uv run search_code.py -n SpaceEngineers.ObjectBuilders class declaration ""

# Core utilities (VRage.Library)
uv run search_code.py -n VRage class declaration ""
```

## Pagination Strategies

### Window Scanning

Sample windows throughout results:

```bash
uv run search_code.py -l 10 -o 0 class usage MyEntity      # Window 1
uv run search_code.py -l 10 -o 200 class usage MyEntity    # Window 2
uv run search_code.py -l 10 -o 400 class usage MyEntity    # Window 3
uv run search_code.py -l 10 -o 600 class usage MyEntity    # Window 4
```

### Binary Search Pattern

Find specific result ranges:

```bash
# Count total
uv run search_code.py -c method usage Update
# Output: 5234

# Check middle
uv run search_code.py -l 1 -o 2617 method usage Update

# Adjust range based on what you find
uv run search_code.py -l 50 -o 2600 method usage Update
```

### Namespace-Sorted Iteration

Results sort by depth then alphabetically, so namespace filtering creates natural groupings:

```bash
# Process one namespace at a time
uv run search_code.py -n Sandbox.Game class usage MyEntity
uv run search_code.py -n VRage class usage MyEntity
uv run search_code.py -n SpaceEngineers class usage MyEntity
```

## Context Management Tips

Keep your queries focused to avoid overwhelming context:

1. **Query 10-20 results max per command** - More is rarely useful
2. **Read selectively** - Don't read every matched file
3. **Use count to estimate scope** - Helps decide if you need to narrow
4. **Prefer declarations over usages** - Definitions are more informative
5. **Sample strategically** - Beginning, middle, end of large result sets
6. **Clear context between major searches** - Don't carry everything forward

## Performance Tips

1. **Signature searches are fastest** - Smaller index, single file
2. **Namespace filtering is cheap** - Apply liberally
3. **Limit aggressively** - `-l 10` is usually enough
4. **Count is instant** - Use it to validate patterns
5. **Regex is fine** - Doesn't impact performance significantly

## Next Steps

- **Basic searches**: See `CodeSearch.md` for fundamentals
- **Hierarchy searches**: See `HierarchySearch.md` for inheritance
- **Technical details**: See `Implementation.md` for how it works
