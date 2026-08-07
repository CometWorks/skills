# Using a Graphify Graph (optional)

> Read this only when a Graphify graph has been built and you want to query it.
> It is optional tooling layered on top of the regular code search, so it stays
> out of context until needed. To build a graph, see
> [GraphifyPrepare.md](GraphifyPrepare.md).

Graphify answers *structural* questions the CSV code index cannot: how symbols connect
(calls, inheritance, references), the shortest relationship path between two symbols,
what a change would impact, and which community (cluster) a symbol belongs to. Use it
alongside — not instead of — the `search_*` code index.

## Before querying: is the graph healthy?

A graph is only usable once clustering has finished. Check first:

```bash
# Linux, from the skill folder
bash ../se-dev/graphify-check.sh Data --deep
```

```bat
REM Windows
call ..\se-dev\GraphifyCheck.bat Data
```

The argument is the directory that *contains* `graphify-out/`. For the code skills
that is `Data` (they graph `Data/Decompiled` but store the graph beside it); other
skills keep the graph inside the graphed tree.

`OK` means ready. `MISSING`/`INCOMPLETE` means it must be (re)built — see
[GraphifyPrepare.md](GraphifyPrepare.md#health-check-and-rebuild). Confirm the rebuild
cost with the user before rebuilding the large game/server graphs.

## Large-graph load cap

Graphify refuses to load a `graph.json` larger than 512 MB by default. The game-code and
server-code graphs are ~540-560 MB, so every `query`/`explain`/`path`/`affected` on them
needs the cap raised:

```bash
export GRAPHIFY_MAX_GRAPH_BYTES=2GB
```

Run graphify from the directory holding `graphify-out/` (for the code skills that is
`Data`) so it finds `graphify-out/graph.json` by default, or pass `--graph <path>`.

## Query commands

```bash
# BFS traversal answering a natural-language question (default 2000-token budget)
graphify query "How is a cube grid built and updated?" --budget 400

# Narrow the traversal to one edge context (repeatable): call, inherits, references, ...
graphify query "MyCubeGrid" --context call --budget 300

# Plain-language explanation of one node and its neighbours (shows its Community)
graphify explain "MyCubeBlock"

# Shortest relationship path between two symbols
graphify path "MyCubeBlock" "MyEntity"

# Reverse traversal: what depends on / is impacted by a symbol
graphify affected "MyEntity" --depth 1
```

Node names are matched fuzzily; `path`/`explain` may warn when a name is ambiguous and
pick the best match. If `query` returns *No matching nodes found*, try a different symbol
or a phrasing that mentions a concrete type/method name.

## Verifying a prepared graph

Each decompiled-code skill ships a query smoke test that runs a representative set of the
commands above (after a health check):

```bash
# Linux
./test_graphify_game_code.sh          # in se-dev-game-code
./test_graphify_server_code.sh        # in se-dev-server-code
```

```bat
REM Windows
.\test_graphify_game_code.bat
.\test_graphify_server_code.bat
```

A healthy run ends with `ALL TESTS COMPLETED`. If it stops at the health check, the graph
is missing or unusable and must be rebuilt.
