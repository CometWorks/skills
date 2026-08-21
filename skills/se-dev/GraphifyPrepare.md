# Prepare-Time Graphify Graphs

> Read this only when the user wants the Graphify graph. It is not needed for
> normal script/mod/plugin/code-search work, so it stays out of context until it
> is actually relevant. For querying an existing graph see
> [GraphifyUsage.md](GraphifyUsage.md).

Each `se-dev-*` prepare script can build a separate [Graphify](https://pypi.org/project/graphifyy/)
graph for the corpus it prepares. The graph is a navigable map (call/inherit/reference
edges plus LLM-named communities) beside the regular search indexes.

## Fast clustering vs. the slow fallback

Building a graph is cheap **except for clustering** (community detection), which is the
long pole on the big corpora. Graphify has two clustering backends:

- **Fast — native Rust Leiden** (`graspologic`, which needs **Python < 3.13**; we use
  3.12). Runs the whole game/server corpus in ~1-2 minutes.
- **Slow — pure-Python Louvain fallback**, used automatically when `graspologic` is not
  importable (e.g. Graphify installed on Python 3.13, where `graspologic` has no wheel).
  It is **single-core** and adds ~10-30 minutes on the ~220k-node game/server graphs.

So prepare defaults the Graphify tool to **Python 3.12 with the `leiden` extra** and picks
its behaviour from which backend is available:

- **Fast backend available** (Linux/Windows with `uv`): prepare **provisions it and builds
  the graph automatically** — no opt-in needed. Because `uv` can fetch Python 3.12 and the
  `graspologic` wheels on demand, this is the normal case.
- **Fast backend cannot be provisioned** (no `uv`, no Python 3.12, or `graspologic` will
  not import): Graphify stays **optional and off**. Prepare skips it and reports the time
  the slow fallback would cost; build anyway by opting in with `SE_DEV_GRAPHIFY=1`.

`SE_DEV_GRAPHIFY` is a tri-state override:

| Value | Effect |
|-------|--------|
| unset | **auto** — build when the fast Rust backend is available, skip otherwise |
| `1`   | **always build**, even on the slow single-core fallback (~10-30 min) |
| `0`   | **never build** — disable Graphify entirely |

The one-time provisioning of the fast backend (uv fetching Python 3.12 + `graspologic`)
takes ~30-60 seconds and is logged. To pin a different interpreter, set
`SE_DEV_GRAPHIFY_PYTHON` (default `3.12`); it must be `< 3.13` for the fast backend.

## Asking the user

On the fast path the graph builds automatically as part of prepare, so there is nothing to
ask — just mention it will be built.

Only when the fast backend is **unavailable** does the cost become significant. In that case
the first time a large corpus is prepared the skill should **ask the user whether to build
the graph on the slow fallback**, stating the expected extra time (see the
[Build time](#build-time) table), and only opt in (`SE_DEV_GRAPHIFY=1`) if they agree.
Skipping costs nothing later — it can be built on a subsequent prepare run at any time.

## Installation

Prepare installs Graphify automatically through `uv` when the fast backend is available. To
install it manually, use the **fast** form (Python 3.12 + `leiden` extra):

```bash
# Recommended; uv fetches Python 3.12 and puts graphify on PATH automatically
uv tool install --python 3.12 'graphifyy[leiden]'

# Alternatives (the leiden extra is only fast on Python 3.12)
pipx install --python python3.12 'graphifyy[leiden]'
pip install 'graphifyy[leiden]'          # run under a Python 3.12 interpreter

# Then install Graphify integration for the active AI platform
graphify install --platform [AI PLATFORM]
```

Installing plain `graphifyy` (no `leiden` extra) or under Python 3.13 gets the slow
single-core clustering fallback.

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

Graph output goes to `<graph root>/graphify-out` unless the skill passes a separate
output directory (third argument of `se_dev_graphify_prepare` / `GraphifyPrepare.bat`).

Both entry points also raise `GRAPHIFY_MAX_GRAPH_BYTES` to `2GB` (an already-set value
wins), because the decompiled game-code and server-code `graph.json` files are far past
Graphify's 512 MB default and every build and update on them would otherwise abort. See
[GraphifyUsage.md](GraphifyUsage.md) for the query-side effect of the same cap.

### Code-only extraction, always

Graphify extracts code with a local AST parser, but doc, paper and image files go
through an LLM. It aborts the **whole** build on the first such file when no backend is
configured — so a single `README.md` or screenshot in the corpus killed the graph for
`se-dev-script`, `se-dev-mod`, `se-dev-plugin` and `se-dev-torch`, whose sources all
carry one. Only the two code skills were unaffected, their corpora being nothing but
decompiled C#.

Every build therefore excludes those file types (`SE_DEV_GRAPHIFY_EXCLUDES` in
`graphify-prepare.sh`, `GRAPHIFY_EXCLUDES` in `GraphifyPrepare.bat`). No API key is used
and no LLM call is ever made. Graphify has no `--code-only` flag and silently ignores
unknown options, so `--exclude` is what actually keeps the build local.

The exclusions cost the code skills nothing: their graphs contain no doc nodes, so an
update reproduces the same node and edge counts.

| Subskill | Default graph root | Graph stored in | Override |
|----------|--------------------|-----------------|----------|
| `se-dev-script` | local PB script folder (`IngameScripts/local`) | inside the graph root | `SE_DEV_SCRIPT_PROJECT_ROOT` |
| `se-dev-mod` | local mod folder (`Mods`) | inside the graph root | `SE_DEV_MOD_PROJECT_ROOT` |
| `se-dev-plugin` | downloaded plugin sources (`Data/Sources`) | inside the graph root | `SE_DEV_PLUGIN_PROJECT_ROOT` |
| `se-dev-torch` | selected Torch checkout (`TORCH_ROOT` or `Data/Sources/Torch`) | inside the graph root | `SE_DEV_TORCH_PLUGIN_ROOT` |
| `se-dev-game-code` | decompiled game code (`Data/Decompiled`) | `Data` (`SE_DEV_GAME_CODE_GRAPH_OUT`) | `SE_DEV_GAME_CODE_GRAPH_ROOT` |
| `se-dev-server-code` | decompiled server code (`Data/Decompiled`) | `Data` (`SE_DEV_SERVER_CODE_GRAPH_OUT`) | `SE_DEV_SERVER_CODE_GRAPH_ROOT` |

Use the override variables when the subskill should graph a specific active project
instead of the default prepared corpus.

## Build time

The Graphify step runs on top of the normal prepare time. Rough numbers:

- **First-ever install on a machine**: a one-time ~30-60 second provisioning (Graphify
  plus Python 3.12, the Rust `graspologic` clustering backend, tree-sitter and numpy).
- **First graph build** (`graphify <root>`): scales with corpus size; clustering dominates.
- **Later runs** (`graphify <root> --update`): incremental re-extraction of changed code
  files only, usually much faster; no LLM needed.

| Subskill | Corpus size | Added build time — fast (Rust Leiden) | Added build time — slow fallback |
|----------|-------------|----------------------------------------|----------------------------------|
| `se-dev-script` | local scripts (usually tiny) | seconds | seconds |
| `se-dev-mod` | local mods | seconds to ~1 min | seconds to a couple of minutes |
| `se-dev-plugin` | downloaded sources | seconds to ~1 min | seconds to a couple of minutes |
| `se-dev-torch` | Torch checkout (~300 files) | under a minute | ~1 minute |
| `se-dev-game-code` | ~10,000 decompiled `.cs` files (~220k-node graph) | ~1-2 minutes | ~10-30 minutes |
| `se-dev-server-code` | ~10,000 decompiled `.cs` files (~220k-node graph) | ~1-2 minutes | ~10-30 minutes |

On the slow fallback the graph build for the two decompiled-code corpora can take as long
as, or longer than, the decompilation itself — which is why that path is opt-in. The fast
Rust backend removes that cost, so on a machine with `uv` the graph is built automatically.

## Disk space

The graph output is large: `graphify-out/` holds `graph.json`, the clustering analysis and
a semantic cache, and together they run roughly **9x the source corpus size**. For the
decompiled game/server code (~175 MB of `.cs`) that is about **1.5 GB per corpus**; the two
graphs together need ~3 GB. Small corpora (scripts, mods, plugins, Torch) are negligible.

On Windows, prepare runs a **disk pre-check** right before building: it requires roughly
`12 x corpus size + 1 GiB` of free space on the graph volume (headroom over the observed
footprint plus room for the code base to grow). If there is not enough free space it logs
how much is needed versus available and **skips the graph build** — core preparation
(decompilation and indexing) has already succeeded, so prepare still finishes. Free up
space and re-run prepare to build the graph later.

## Health check and rebuild

A graph is only usable once **clustering** finishes. Clustering writes
`graphify-out/.graphify_analysis.json`; without it every node has an empty community and
queries return little useful structure. A build that is killed part-way leaves a
`graph.json` with no clustering — an **incomplete, unusable** graph. (The fast backend makes
this far less likely, since clustering the big corpora now takes only a minute or two.)

Prepare guards against this automatically: it inspects an existing graph and, if it finds
`graph.json` but no clustering (or a truncated `graph.json`), it **cleans `graphify-out/`
and rebuilds from scratch** rather than `--update`-ing a broken graph.

The same inspection decides whether to touch the graph at all. A subskill that knows
nothing in its corpus was regenerated passes `unchanged` as the fourth argument of
`se_dev_graphify_prepare` / `GraphifyPrepare.bat`; a healthy graph is then **left alone**,
skipping the tool provisioning, the disk pre-check and the incremental rescan. An unhealthy
or missing graph is still rebuilt. `se-dev-game-code` and `se-dev-server-code` pass
`unchanged` whenever the game version is the same and nothing under `Data` was rebuilt, so
repeated prepare runs on an up-to-date install finish in seconds.

To check a graph's health independently, run the standalone checker:

```bash
# Linux (from the skill folder)
bash ../se-dev/graphify-check.sh Data          # fast: file presence
bash ../se-dev/graphify-check.sh Data --deep   # also validates clustering content
```

```bat
REM Windows
call ..\se-dev\GraphifyCheck.bat Data
```

The argument is the directory that *contains* `graphify-out/`. For the code skills
that is `Data` (they graph `Data/Decompiled` but store the graph beside it); other
skills keep the graph inside the graphed tree.

Exit codes: `0` ok, `2` missing (never built), `3` incomplete (must be rebuilt). If it
reports `incomplete` or `missing` and you want the graph, delete `graphify-out/` and re-run
prepare — it rebuilds automatically with the fast Rust backend. On a machine without that
backend the rebuild uses the slow fallback (~10-30 min for game/server code) and must be
opted in with `SE_DEV_GRAPHIFY=1`; **confirm with the user first** in that case.

## Corpus content and API keys

Prepare always builds a **code-only** graph and never uses an API key. Graphify treats
`.md`, `.txt`, `.rst`, `.yaml`, `.yml`, `.html` and similar files as *documents* that
need LLM-based semantic extraction, and its build fails if any are present and no key
(`ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, …) is set — prepare excludes them, see
[Code-only extraction, always](#code-only-extraction-always). Outside prepare, run
`graphify` yourself with the same `--exclude` globs, or add a `.graphifyignore`
(gitignore syntax) at the graph root excluding the doc extensions.

## Failure behavior

Graphify is supplemental. Prepare logs a warning and continues if:

- Graphify is disabled (`SE_DEV_GRAPHIFY=0`),
- the fast backend is unavailable and the user did not opt in (`SE_DEV_GRAPHIFY` not `1`),
- the user declines installation on the slow-fallback path,
- `graphify` is not on `PATH` after installation,
- the selected graph root does not exist,
- graph creation or update fails.

A missing LLM API key is not one of these: prepare always excludes the doc/paper/image
files (see [Code-only extraction, always](#code-only-extraction-always)).

Core preparation still succeeds when indexing or decompilation succeeds.
