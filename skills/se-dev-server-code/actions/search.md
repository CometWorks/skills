# Search Action

> **Part of the se-dev-server-code skill.** Invoked when searching the server's decompiled code.

Run searches using `uv run search_server_code.py` from this skill folder.

## Quick Reference

```cmd
uv run search_server_code.py --help
```

## Documentation

For complete search documentation:

- **[QuickStart.md](../QuickStart.md)** - More examples and quick reference
- **[CodeSearch.md](../CodeSearch.md)** - Complete guide to searching classes, methods, fields, etc.
- **[HierarchySearch.md](../HierarchySearch.md)** - Finding class/interface inheritance and implementations
- **[Advanced.md](../Advanced.md)** - Power user techniques for complex searches
- **[Implementation.md](../Implementation.md)** - Technical details for skill contributors (optional)

## When to Search

Always check server code when:
- Unsure about server's internal APIs and how to interface with them.
- Inner workings of Space Engineers Dedicated Server unclear.

## Search Targets

- **Data/Decompiled folder** - Search C# source files (*.cs) in general. For transpiler or preloader patches, also search IL code (*.il) files.
- **Data/Content folder** - Search server content data files. See [ContentTypes.md](../ContentTypes.md) for list of types.
