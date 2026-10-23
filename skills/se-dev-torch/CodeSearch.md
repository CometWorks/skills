# Code Search

Torch skill indexes selected Torch repository into CSV files under `Data/CodeIndex`.

Use `uv run search_torch.py ...` from this skill folder.

## Symbol categories

Supported categories:

- `namespace`
- `interface`
- `class`
- `struct`
- `enum`
- `method`
- `field`
- `property`
- `event`
- `constructor`

Supported search modes:

- `declaration`
- `usage`
- `signature` for methods
- `parent`, `children`, `implements`, `implementors` for hierarchy queries

## Basic examples

```bash
# Class and interface declarations
uv run search_torch.py class declaration TorchPluginBase
uv run search_torch.py interface declaration ITorchPlugin

# Usages
uv run search_torch.py class usage CommandManager
uv run search_torch.py method usage RegisterPluginCommands

# Method signatures
uv run search_torch.py method signature Init
uv run search_torch.py method signature InvokeAsync -n Torch.API
```

## Namespace filters

Use `-n` to narrow by namespace prefix:

```bash
uv run search_torch.py interface declaration IManager -n Torch.API.Managers
uv run search_torch.py class declaration PluginManager -n Torch.Managers
uv run search_torch.py class declaration TorchServer -n Torch.Server
```

## Count, limit, and pagination

```bash
uv run search_torch.py class usage Manager --count
uv run search_torch.py class usage Manager --limit 20
uv run search_torch.py class usage Manager --limit 20 --offset 20
```

## Regex and case-insensitive search

```bash
uv run search_torch.py method declaration re:.*Command
uv run search_torch.py class declaration plugin -i
```

If you omit `text:` or `re:`, plain text matching used.

## Hierarchy and implementation queries

```bash
uv run search_torch.py class children Manager
uv run search_torch.py interface implementors ITorchPlugin
uv run search_torch.py class implements TorchPluginBase
```

Hierarchy files also written as text trees:

- `Data/CodeIndex/class_hierarchy.txt`
- `Data/CodeIndex/interface_hierarchy.txt`

## Output interpretation

- `declaration` and `usage` print `file_path:start_line-end_line` (`file_path:line` for one line).
- `method signature` prints `location|signature`.
- `parent` and `implements` print `type:parent` / `type:interfaces`; `children` and `implementors` print `parent|children`, children grouped by namespace as `Namespace.(A,B)`.
- `file_path` is relative to Torch repository root chosen during preparation.
- No match prints `NO-MATCHES`.

## Search strategy

1. Start with declarations for framework types you expect.
2. Use method signatures to locate extension points.
3. Switch to usages to find concrete patterns.
4. Add `-n` early when you know subsystem.
5. Use `--count` before broad searches like `Manager`, `Plugin`, or `Command`.
