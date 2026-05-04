#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../../scripts/common-posix.sh
source "$SCRIPT_DIR/../../scripts/common-posix.sh"

cd "$SCRIPT_DIR"

log "Verifying Python"
require_python_3_13
log "Verifying git"
require_cmd git
ensure_uv
ensure_uv_sync

DATA_ROOT="$(default_data_home)/plugin"
log "Data Root: $DATA_ROOT"
ensure_directory_link "Data" "$DATA_ROOT"
mkdir -p Data/Sources

log "Updating PluginHub registry"
uv run python -u download_pluginhub.py

log "Indexing plugin code (skipped if no sources cloned yet)"
uv run python -u index_plugins.py

: >Prepare.DONE
log "DONE"
