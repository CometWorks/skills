#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMMON_POSIX_SH="$SCRIPT_DIR/common-posix.sh"
if [ ! -f "$COMMON_POSIX_SH" ]; then
    COMMON_POSIX_SH="$SCRIPT_DIR/../../scripts/common-posix.sh"
fi
# shellcheck source=./common-posix.sh
source "$COMMON_POSIX_SH"
# shellcheck source=../se-dev/graphify-prepare.sh
source "$SCRIPT_DIR/../se-dev/graphify-prepare.sh"

cd "$SCRIPT_DIR"

log "Verifying Python"
require_python_3_11
log "Verifying git"
require_cmd git
ensure_uv
ensure_uv_sync

DATA_ROOT="$(default_data_home)/torch"
log "Data Root: $DATA_ROOT"
ensure_directory_link "Data" "$DATA_ROOT"
mkdir -p Data/Sources Data/CodeIndex

TORCH_CLONE_DIR="Data/Sources/Torch"
if [ -n "${TORCH_ROOT:-}" ]; then
    [ -d "$TORCH_ROOT" ] || fail "TORCH_ROOT does not exist: $TORCH_ROOT"
    [ -f "$TORCH_ROOT/Torch.sln" ] || fail "TORCH_ROOT must point at the Torch repository root containing Torch.sln."
    TORCH_SOURCE="$(cd -P -- "$TORCH_ROOT" && pwd)"
    log "Using local Torch checkout: $TORCH_SOURCE"
else
    if [ -d "$TORCH_CLONE_DIR/.git" ]; then
        log "Updating Torch checkout"
        git -C "$TORCH_CLONE_DIR" pull --ff-only
    elif [ -e "$TORCH_CLONE_DIR" ]; then
        fail "$TORCH_CLONE_DIR exists but is not a git checkout."
    else
        log "Cloning TorchAPI/Torch"
        git clone https://github.com/TorchAPI/Torch.git "$TORCH_CLONE_DIR"
    fi
    TORCH_SOURCE="$(cd -P -- "$TORCH_CLONE_DIR" && pwd)"
    log "Using cloned Torch checkout: $TORCH_SOURCE"
fi

printf '%s\n' "$TORCH_SOURCE" > Data/torch_root.txt

log "Indexing Torch source"
uv run python -u index_torch.py

TORCH_GRAPH_ROOT="${SE_DEV_TORCH_PLUGIN_ROOT:-$TORCH_SOURCE}"
se_dev_graphify_prepare "se-dev-torch" "$TORCH_GRAPH_ROOT"

: >Prepare.DONE
log "DONE"
