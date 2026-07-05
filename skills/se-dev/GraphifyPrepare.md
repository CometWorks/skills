# Prepare-Time Graphify Graphs (optional)

> Read this only when the user wants the optional Graphify graph. It is not
> needed for normal script/mod/plugin/code-search work, so it stays out of
> context until it is actually relevant. For querying an existing graph see
> [GraphifyUsage.md](GraphifyUsage.md).

Each `se-dev-*` prepare script can build a separate [Graphify](https://pypi.org/project/graphifyy/)
graph for the corpus it prepares. The graph is a navigable map (call/inherit/reference
edges plus LLM-named communities) beside the regular search indexes.

**Graphify is strictly optional and OFF by default.** Building it — especially over
the ~10,000-file decompiled game/server corpora — can add ~10-30 minutes on top of the
normal prepare, and if the build is interrupted the result is unusable and must be
redone from scratch. So prepare never builds it unless the user opts in.

## Asking the user (first prepare)

Because the cost is significant, the very first time a corpus is prepared the skill
should **ask the user whether to also build the Graphify graph**, and only build it if
they say yes. When asking, state the expected extra time for that corpus (see the
[Build time](#build-time) table). Do not build it silently.

- **User declines (default):** run prepare normally. Graphify is skipped; the log shows
  `Graphify: skipping <label> (set SE_DEV_GRAPHIFY=1 to build the optional graph)`.
- **User opts in:** set `SE_DEV_GRAPHIFY=1` for that prepare run, e.g.
  `SE_DEV_GRAPHIFY=1 ./prepare.sh` (Linux) or `set SE_DEV_GRAPHIFY=1` then `.\Prepare.bat`
  (Windows).

Skipping Graphify costs nothing later — it can be built on a subsequent prepare run at
any time by opting in.

## Installation

When opted in, if `graphify` is not on `PATH`, prepare offers to install it:

```bash
# Recommended; uv puts graphify on PATH automatically
uv tool install graphifyy

# Alternatives
pipx install graphifyy
pip install graphifyy

# Then install Graphify integration for the active AI platform
graphify install --platform [AI PLATFORM]
```

Set `SE_DEV_GRAPHIFY_PLATFORM` before prepare to run the platform install automatically
after the package is installed:

```bash
export SE_DEV_GRAPHIFY_PLATFORM=codex     # Linux
```

```bat
set SE_DEV_GRAPHIFY_PLATFORM=codex        REM Windows
```

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

Use the override variables when the subskill should graph a specific active project
instead of the default prepared corpus.

## Build time

The Graphify step runs on top of the normal prepare time. Rough numbers:

- **First-ever install on a machine**: a one-time ~30 second download (Graphify plus its
  tree-sitter and numpy dependencies).
- **First graph build** (`graphify <root>`): scales with corpus size.
- **Later runs** (`graphify <root> --update`): incremental re-extraction of changed code
  files only, usually much faster; no LLM needed.

| Subskill | Corpus size | Added graph-build time (first run) |
|----------|-------------|------------------------------------|
| `se-dev-script` | local scripts (usually tiny) | seconds |
| `se-dev-mod` | local mods | seconds to a couple of minutes (scales with mod count) |
| `se-dev-plugin` | downloaded sources | seconds to a couple of minutes (scales with plugin count) |
| `se-dev-torch` | Torch checkout (~300 files) | ~1 minute |
| `se-dev-game-code` | ~10,000 decompiled `.cs` files | ~10-30 minutes (~220k-node graph) |
| `se-dev-server-code` | ~10,000 decompiled `.cs` files | ~10-30 minutes (~220k-node graph) |

For the two decompiled-code corpora the graph build can take as long as, or longer than,
the decompilation itself — the main reason it is opt-in.

## Disk space

The graph output is large: `graphify-out/` holds `graph.json`, the clustering analysis and
a semantic cache, and together they run roughly **9x the source corpus size**. For the
decompiled game/server code (~175 MB of `.cs`) that is about **1.5 GB per corpus**; the two
graphs together need ~3 GB. Small corpora (scripts, mods, plugins, Torch) are negligible.

When opted in, prepare runs a **disk pre-check** right before building: it requires roughly
`12 x corpus size + 1 GiB` of free space on the graph volume (headroom over the observed
footprint plus room for the code base to grow). If there is not enough free space it logs
how much is needed versus available and **skips the graph build** — core preparation
(decompilation and indexing) has already succeeded, so prepare still finishes. Free up
space and re-run prepare with `SE_DEV_GRAPHIFY=1` to build the graph later.

## Health check and rebuild

A graph is only usable once **clustering** finishes. Clustering writes
`graphify-out/.graphify_analysis.json`; without it every node has an empty community and
queries return little useful structure. A build that is killed part-way (common for the
large corpora) leaves a `graph.json` with no clustering — an **incomplete, unusable**
graph.

Prepare guards against this automatically: when opted in, it inspects an existing graph
and, if it finds `graph.json` but no clustering, it **cleans `graphify-out/` and rebuilds
from scratch** rather than `--update`-ing a broken graph.

To check a graph's health independently, run the standalone checker:

```bash
# Linux (from the skill folder)
bash ../se-dev/graphify-check.sh Data/Decompiled          # fast: file presence
bash ../se-dev/graphify-check.sh Data/Decompiled --deep   # also validates clustering content
```

```bat
REM Windows
call ..\se-dev\GraphifyCheck.bat Data\Decompiled
```

Exit codes: `0` ok, `2` missing (never built), `3` incomplete (must be rebuilt). If it
reports `incomplete` or `missing` and you want the graph, delete `graphify-out/` and
re-run prepare with `SE_DEV_GRAPHIFY=1`. **Confirm with the user first** — rebuilding the
game/server graph costs ~10-30 minutes.

## Corpus content and API keys

Graphify builds a **code-only** graph with no API key. It treats `.md`, `.txt`, `.rst`,
`.yaml`, `.yml`, `.html` and similar files as *documents* that need LLM-based semantic
extraction, and the build fails if any are present and no key (`ANTHROPIC_API_KEY`,
`GEMINI_API_KEY`, …) is set. The decompiled game/server corpora are pure `.cs` and build
keyless, but mixed corpora (e.g. a Torch checkout with `README.md`) do not. To graph only
the code in a mixed corpus without a key, add a `.graphifyignore` (gitignore syntax) at
the graph root excluding the doc extensions.

## Failure behavior

Graphify is supplemental. Prepare logs a warning and continues if:

- the user did not opt in (`SE_DEV_GRAPHIFY` not `1`),
- the user declines installation,
- `graphify` is not on `PATH` after installation,
- the selected graph root does not exist,
- graph creation or update fails.

Core preparation still succeeds when indexing or decompilation succeeds.
