# Search Action

> **Part of the se-dev-game-code skill.** Invoked when searching the game's decompiled code.

Run searches using `uv run search_game_code.py` from this skill folder.

## Quick Reference

```cmd
uv run search_game_code.py --help
```

## Documentation

For full search documentation, see:

- **[QuickStart.md](../QuickStart.md)** - More examples and quick reference
- **[CodeSearch.md](../CodeSearch.md)** - Full guide to searching classes, methods, fields, etc.
- **[HierarchySearch.md](../HierarchySearch.md)** - Find class/interface inheritance and implementations
- **[Advanced.md](../Advanced.md)** - Power user techniques for complex searches
- **[Implementation.md](../Implementation.md)** - Technical details for skill contributors (optional)

## When to Search

Always check game code when:
- Unsure about game's internal APIs and how to interface with them.
- Inner workings of Space Engineers unclear.

## Search Targets

- **Data/Decompiled folder** - Search C# source files (*.cs) in general. For transpiler or preloader patches, also search IL code (*.il) files.
- **Data/Content folder** - Search game content data files. See [ContentTypes.md](../ContentTypes.md) for list of types.
