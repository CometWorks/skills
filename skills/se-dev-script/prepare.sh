#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common-posix.sh
source "$SCRIPT_DIR/common-posix.sh"

cd "$SCRIPT_DIR"

log "Verifying Python"
require_python_3_11
ensure_uv
ensure_uv_sync

DATA_ROOT="$(default_data_home)/script"
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
LOCAL_SCRIPTS_TARGET="$APPDATA_DIR/IngameScripts/local"
mkdir -p "$LOCAL_SCRIPTS_TARGET"
ensure_directory_link "LocalScripts" "$LOCAL_SCRIPTS_TARGET"

log "Building script inventory"
uv run python -u list_scripts.py

log "Indexing script code (incremental: only changed scripts are reparsed)"
uv run python -u index_scripts.py

: >Prepare.DONE
log "DONE"
