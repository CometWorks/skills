# Prepare-Time Graphify Graphs

Each `se-dev-*` prepare script can build a separate Graphify graph for the corpus prepared by that subskill. Graphify is optional, but highly recommended because it creates a navigable map beside the regular search indexes.

If `graphify` is available on `PATH`, prepare runs it automatically for the active subskill. If `graphify-out/graph.json` already exists under that corpus root, prepare runs `graphify <root> --update`; otherwise it runs `graphify <root>`.

If `graphify` is missing, prepare prompts the user to install it:

```bash
# Recommended; uv puts graphify on PATH automatically
uv tool install graphifyy

# Alternatives
pipx install graphifyy
pip install graphifyy

# Then install Graphify integration for the active AI platform
graphify install --platform [AI PLATFORM]
```

Set `SE_DEV_GRAPHIFY_PLATFORM` before prepare to let the helper run the platform install automatically after package installation:

```bash
export SE_DEV_GRAPHIFY_PLATFORM=codex
```

On Windows:

```bat
set SE_DEV_GRAPHIFY_PLATFORM=codex
```

Set `SE_DEV_GRAPHIFY=0` to skip Graphify during prepare.

## Graph roots

Prepare builds one graph per subskill, under that root's own `graphify-out/` directory:

| Subskill | Default graph root | Override |
|----------|--------------------|----------|
| `se-dev-script` | local PB script folder (`IngameScripts/local`) | `SE_DEV_SCRIPT_PROJECT_ROOT` |
| `se-dev-mod` | local mod folder (`Mods`) | `SE_DEV_MOD_PROJECT_ROOT` |
| `se-dev-plugin` | downloaded plugin sources (`Data/Sources`) | `SE_DEV_PLUGIN_PROJECT_ROOT` |
| `se-dev-torch` | selected Torch checkout (`TORCH_ROOT` or `Data/Sources/Torch`) | `SE_DEV_TORCH_PLUGIN_ROOT` |
| `se-dev-game-code` | decompiled game code (`Data/Decompiled`) | `SE_DEV_GAME_CODE_GRAPH_ROOT` |
| `se-dev-server-code` | decompiled server code (`Data/Decompiled`) | `SE_DEV_SERVER_CODE_GRAPH_ROOT` |

Use the override variables when the subskill should graph a specific active project instead of the default prepared corpus.

## Failure behavior

Graphify is supplemental. Prepare logs a warning and continues if:

- the user declines installation,
- `graphify` is not on `PATH` after installation,
- the selected graph root does not exist,
- graph creation or update fails.

Core preparation still succeeds when indexing or decompilation succeeds.
