#!/usr/bin/env bash
#
# Graphify query smoke test for the decompiled dedicated-server graph.
#
# Mirrors test_search_server_code.sh (which tests the CSV code index) but
# exercises the optional Graphify graph instead: it first verifies the graph is
# healthy (built and clustered), then runs a handful of query / explain / path /
# affected calls to confirm the graph answers questions.
#
# The server-code graph.json is larger than Graphify's default 512 MB load cap,
# so GRAPHIFY_MAX_GRAPH_BYTES is raised here.

set -u
cd "$(dirname "$(readlink -f "$0")")"

SKILL_DIR="$(pwd)"
GRAPH_ROOT="${SE_DEV_SERVER_CODE_GRAPH_ROOT:-Data/Decompiled}"
export GRAPHIFY_MAX_GRAPH_BYTES="${GRAPHIFY_MAX_GRAPH_BYTES:-2GB}"

echo ============================================================
echo GRAPHIFY HEALTH CHECK
echo ============================================================
if ! command -v graphify >/dev/null 2>&1; then
    echo "SKIP: graphify is not on PATH. Build the graph with:"
    echo "  SE_DEV_GRAPHIFY=1 ./prepare.sh"
    exit 1
fi
if ! bash "$SKILL_DIR/../se-dev/graphify-check.sh" "$GRAPH_ROOT" --deep; then
    echo
    echo "FAIL: Graphify graph is missing or unusable. Rebuild it with:"
    echo "  rm -rf \"$GRAPH_ROOT/graphify-out\""
    echo "  SE_DEV_GRAPHIFY=1 ./prepare.sh"
    exit 1
fi
echo

# All graphify subcommands default to graphify-out/graph.json under the cwd.
cd "$GRAPH_ROOT"

echo ============================================================
echo QUERY - BFS traversal for a question
echo ============================================================
echo "--- How does the dedicated server start a session? ---"
graphify query "How does the dedicated server start a session?" --budget 400
echo
echo "--- How does the server handle multiplayer clients? ---"
graphify query "How does the server handle multiplayer clients?" --budget 400
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
echo "--- Explain MySession ---"
graphify explain "MySession"
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
