#!/usr/bin/env bash
#
# Graphify query smoke test for the decompiled game-code graph (Linux).
#
# Mirrors test_search_game_code.sh (which tests the CSV code index) but exercises
# the optional Graphify graph instead: it first verifies the graph is healthy
# (built and clustered), then runs the asserted query / explain / path / affected
# checks in test_graphify_queries.py, shared with the Windows wrapper.
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

uv run test_graphify_queries.py "$GRAPH_OUT"
