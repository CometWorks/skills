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

PLUGIN_GRAPH_ROOT="${SE_DEV_PLUGIN_PROJECT_ROOT:-Data/Sources}"
se_dev_graphify_prepare "se-dev-plugin" "$PLUGIN_GRAPH_ROOT"

: >Prepare.DONE
log "DONE"
