#!/usr/bin/env bash
#
# Graphify query smoke test for the decompiled game-code graph.
#
# Mirrors test_search_game_code.sh (which tests the CSV code index) but exercises
# the optional Graphify graph instead: it first verifies the graph is healthy
# (built and clustered), then runs a handful of query / explain / path / affected
# calls to confirm the graph answers questions.
#
# The game-code graph.json is larger than Graphify's default 512 MB load cap, so
# GRAPHIFY_MAX_GRAPH_BYTES is raised here.

set -u
cd "$(dirname "$(readlink -f "$0")")"

SKILL_DIR="$(pwd)"
GRAPH_ROOT="${SE_DEV_GAME_CODE_GRAPH_ROOT:-Data/Decompiled}"
# graphify-out sits beside Decompiled, not inside it.
GRAPH_OUT="${SE_DEV_GAME_CODE_GRAPH_OUT:-Data}"
export GRAPHIFY_MAX_GRAPH_BYTES="${GRAPHIFY_MAX_GRAPH_BYTES:-2GB}"

echo ============================================================
echo GRAPHIFY HEALTH CHECK
echo ============================================================
if ! command -v graphify >/dev/null 2>&1; then
    echo "SKIP: graphify is not on PATH. Build the graph by running prepare:"
    echo "  ./prepare.sh   # auto-builds with the fast Rust backend; add SE_DEV_GRAPHIFY=1 to force the slow fallback"
    exit 1
fi
if ! bash "$SKILL_DIR/../se-dev/graphify-check.sh" "$GRAPH_OUT" --deep; then
    echo
    echo "FAIL: Graphify graph is missing or unusable. Rebuild it by re-running prepare:"
    echo "  rm -rf \"$GRAPH_OUT/graphify-out\""
    echo "  ./prepare.sh   # auto-builds with the fast Rust backend; add SE_DEV_GRAPHIFY=1 to force the slow fallback"
    exit 1
fi
echo

# All graphify subcommands default to graphify-out/graph.json under the cwd.
cd "$GRAPH_OUT"

echo ============================================================
echo QUERY - BFS traversal for a question
echo ============================================================
echo "--- How is a cube grid built and updated? ---"
graphify query "How is a cube grid built and updated?" --budget 400
echo
echo "--- How does a projector project a blueprint? ---"
graphify query "How does a projector project a blueprint?" --budget 400
echo

echo ============================================================
echo QUERY - narrowed by edge context
echo ============================================================
echo "--- Call edges out of MyCubeGrid ---"
graphify query "MyCubeGrid" --context call --budget 300
echo

echo ============================================================
echo EXPLAIN - a node and its neighbours
echo ============================================================
echo "--- Explain MyCubeBlock ---"
graphify explain "MyCubeBlock"
echo
echo "--- Explain MyEntity ---"
graphify explain "MyEntity"
echo

echo ============================================================
echo PATH - shortest path between two nodes
echo ============================================================
echo "--- MyCubeBlock -> MyEntity ---"
graphify path "MyCubeBlock" "MyEntity"
echo

echo ============================================================
echo AFFECTED - reverse traversal for impact
echo ============================================================
echo "--- What is affected by MyEntity? ---"
graphify affected "MyEntity" --depth 1
echo

echo ============================================================
echo ALL TESTS COMPLETED
echo ============================================================
