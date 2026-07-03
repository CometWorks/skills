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

## Build time

The Graphify step runs on top of the normal prepare time. Rough numbers:

- **First-ever prepare on a machine**: if `graphify` is not yet installed, the install adds a one-time ~30 second download (Graphify plus its tree-sitter and numpy dependencies).
- **First graph build** (`graphify <root>`): scales with corpus size.
- **Later runs** (`graphify <root> --update`): incremental re-extraction of changed code files only, usually much faster; no LLM needed.

| Subskill | Corpus size | Added graph-build time (first run) |
|----------|-------------|------------------------------------|
| `se-dev-script` | local scripts (usually tiny) | seconds |
| `se-dev-mod` | local mods | seconds to a couple of minutes (scales with mod count) |
| `se-dev-plugin` | downloaded sources | seconds to a couple of minutes (scales with plugin count) |
| `se-dev-torch` | Torch checkout (~300 files) | ~1 minute |
| `se-dev-game-code` | ~10,000 decompiled `.cs` files | ~10-30 minutes (~220k-node graph) |
| `se-dev-server-code` | ~10,000 decompiled `.cs` files | ~10-30 minutes (~220k-node graph) |

For the two decompiled-code corpora the graph build can take as long as, or longer than, the decompilation itself. Set `SE_DEV_GRAPHIFY=0` to skip it when a fast prepare matters.

## Corpus content and API keys

Graphify builds a **code-only** graph with no API key. It treats `.md`, `.txt`, `.rst`, `.yaml`, `.yml`, `.html` and similar files as *documents* that need LLM-based semantic extraction, and the build fails if any are present and no key (`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, …) is set. The decompiled game/server corpora are pure `.cs` and build keyless, but mixed corpora (e.g. a Torch checkout with `README.md`) do not. To graph only the code in a mixed corpus without a key, add a `.graphifyignore` (gitignore syntax) at the graph root excluding the doc extensions.

## Querying large graphs

Graphify refuses to load a `graph.json` larger than 512 MB by default. The game-code and server-code graphs are ~540-560 MB, so `graphify query`/`explain`/`path` on them require raising the cap, e.g. `GRAPHIFY_MAX_GRAPH_BYTES=1GB`.

## Failure behavior

Graphify is supplemental. Prepare logs a warning and continues if:

- the user declines installation,
- `graphify` is not on `PATH` after installation,
- the selected graph root does not exist,
- graph creation or update fails.

Core preparation still succeeds when indexing or decompilation succeeds.
