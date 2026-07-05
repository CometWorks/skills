#!/usr/bin/env bash

# Standalone Graphify health check.
#
# Usage: graphify-check.sh <graph-root> [--deep]
#
#   <graph-root>  Directory that was graphed, i.e. the one containing
#                 graphify-out/ (e.g. Data/Decompiled). Defaults to Data/Decompiled.
#   --deep        Also parse graphify-out/.graphify_analysis.json and confirm it
#                 holds a non-empty set of communities, i.e. clustering produced
#                 real content rather than an empty stub. Needs python3.
#
# To actually exercise queries against a prepared corpus, use that skill's
# test_graphify_*.sh script, which runs domain-specific query/explain/path calls.
#
# Exit codes:
#   0  ok          - graph.json plus clustering data present (and usable with --deep)
#   2  missing     - no graph has been built yet
#   3  incomplete  - graph.json present but clustering is missing/interrupted;
#                    the graph must be cleaned and rebuilt from scratch
#
# On a non-zero result the graph is unusable and should be rebuilt. Rebuild is
# expensive for the decompiled game/server corpora (~10-30 minutes), so confirm
# with the user before doing it.

set -u

log() { printf '%s\n' "$*"; }

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./graphify-prepare.sh
source "$SCRIPT_DIR/graphify-prepare.sh"

ROOT="Data/Decompiled"
DEEP=0
for arg in "$@"; do
    case "$arg" in
        --deep) DEEP=1 ;;
        *) ROOT="$arg" ;;
    esac
done

if [ ! -d "$ROOT" ]; then
    log "FAIL: graph root does not exist: $ROOT"
    log "Run prepare first (it builds the graph automatically when the fast Rust backend is available; otherwise set SE_DEV_GRAPHIFY=1)."
    exit 2
fi

ROOT="$(cd -P -- "$ROOT" && pwd)"
STATUS="$(se_dev_graphify_status "$ROOT")"

case "$STATUS" in
    missing)
        log "MISSING: no Graphify graph at $ROOT/graphify-out"
        log "Build it by running prepare (auto-builds with the fast Rust backend; otherwise set SE_DEV_GRAPHIFY=1)."
        exit 2
        ;;
    incomplete)
        log "INCOMPLETE: $ROOT/graphify-out has a graph.json but clustering data is missing."
        log "The graph is unusable and must be rebuilt from scratch."
        log "Clean and rebuild by re-running prepare (fast with the Rust backend; ~10-30 min on the slow fallback for game/server code):"
        log "  rm -rf \"$ROOT/graphify-out\""
        log "  <prepare script>   # add SE_DEV_GRAPHIFY=1 to force a build on the slow fallback"
        exit 3
        ;;
    ok)
        log "OK: graph.json and clustering data present at $ROOT/graphify-out"
        ;;
esac

if [ "$DEEP" = "1" ]; then
    PY="$(command -v python3 || command -v python || true)"
    if [ -z "$PY" ]; then
        log "WARNING: python3 not on PATH; skipping deep clustering check."
        exit 0
    fi
    log "Deep check: validating clustering content in .graphify_analysis.json..."
    if "$PY" - "$ROOT/graphify-out/.graphify_analysis.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print(f"  could not parse analysis file: {e}")
    raise SystemExit(1)
communities = d.get("communities") if isinstance(d, dict) else None
if not communities:
    print("  analysis file has no communities")
    raise SystemExit(1)
print(f"  {len(communities)} communities present")
raise SystemExit(0)
PY
    then
        log "OK: clustering data is populated."
    else
        log "INCOMPLETE: clustering data is empty or corrupt; the graph is unusable."
        log "Clean and rebuild the graph as above."
        exit 3
    fi
fi

exit 0
