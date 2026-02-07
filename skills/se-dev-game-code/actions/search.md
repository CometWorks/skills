# Search Action

> **Part of the se-dev-game-code skill.** Invoked when searching the game's decompiled code.

Run searches using `uv run search_code.py` from this skill folder.

## Quick Reference

```cmd
uv run search_code.py --help
```

## Documentation

For complete search documentation, see:

- **[QuickStart.md](../QuickStart.md)** - More examples and quick reference
- **[CodeSearch.md](../CodeSearch.md)** - Complete guide to searching classes, methods, fields, etc.
- **[HierarchySearch.md](../HierarchySearch.md)** - Finding class/interface inheritance and implementations
- **[Advanced.md](../Advanced.md)** - Power user techniques for complex searches
- **[Implementation.md](../Implementation.md)** - Technical details for skill contributors (optional)

## When to Search

Always check the game code when:
- You're unsure about the game's internal APIs and how to interface with them.
- The inner workings of Space Engineers is unclear.

## Search Targets

- **Decompiled folder** - Search C# source files (*.cs) in general. For transpiler or preloader patches, also search IL code (*.il) files.
- **Content folder** - Search game content data files. See [ContentTypes.md](../ContentTypes.md) for the list of types.
