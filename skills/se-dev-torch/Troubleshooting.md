# Troubleshooting

## `Prepare` fails

Check these first:

1. `python --version` is at least 3.13
2. `git --version` works
3. If using `TORCH_ROOT`, it points at the Torch repository root and contains `Torch.sln`
4. `Prepare.log` ends with `DONE`

## Search returns `NO-MATCHES`

Check:

1. The skill was prepared after selecting or updating the Torch source root
2. `Data/torch_root.txt` points at the expected checkout
3. You are searching the right namespace with `-n`
4. You are using the right symbol category (`class`, `interface`, `method`, etc.)

Broad symbols like `Manager`, `Plugin`, and `Command` usually need a namespace filter.

## Search results are stale

Re-run:

```bash
./Prepare.sh
```

or:

```bash
uv run index_torch.py
```

Use preparation again if you changed `TORCH_ROOT`.

## The answer needs Keen internals, not Torch internals

This skill only indexes the Torch repository. Pair it with:

- `se-dev-game-code`
- `se-dev-server-code`

## The code uses obsolete APIs

Torch still contains older APIs and compatibility paths. When you see both options:

- prefer `manifest.xml` over `PluginAttribute`
- prefer `Managers.GetManager<T>()` over obsolete `GetManager<T>()`

Always confirm the current implementation in the indexed source before advising a migration.
