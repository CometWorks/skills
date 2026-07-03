#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common-posix.sh
source "$SCRIPT_DIR/common-posix.sh"
# shellcheck source=../se-dev/graphify-prepare.sh
source "$SCRIPT_DIR/../se-dev/graphify-prepare.sh"

cd "$SCRIPT_DIR"

log "Verifying Python"
require_python_3_11
ensure_uv
ensure_uv_sync

DATA_ROOT="$(default_data_home)/mod"
log "Data Root: $DATA_ROOT"
ensure_directory_link "Data" "$DATA_ROOT"

GAME_ROOT="$(detect_game_root 2>/dev/null || true)"
if [ -z "$GAME_ROOT" ]; then
    fail "Could not detect Space Engineers install location. Set SE_GAME_ROOT."
fi
APPDATA_DIR="$(detect_se_appdata_dir "$GAME_ROOT" 2>/dev/null || true)"
if [ -z "$APPDATA_DIR" ]; then
    fail "Could not detect Space Engineers appdata folder. Set SE_APPDATA_DIR."
fi
LOCAL_MODS_TARGET="$APPDATA_DIR/Mods"
mkdir -p "$LOCAL_MODS_TARGET"
ensure_directory_link "LocalMods" "$LOCAL_MODS_TARGET"

log "Building mod inventory"
uv run python -u list_mods.py

log "Indexing mod code (incremental: only changed mods are reparsed)"
uv run python -u index_mods.py

MOD_GRAPH_ROOT="${SE_DEV_MOD_PROJECT_ROOT:-$LOCAL_MODS_TARGET}"
se_dev_graphify_prepare "se-dev-mod" "$MOD_GRAPH_ROOT"

: >Prepare.DONE
log "DONE"
