#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
COMMON_POSIX_SH="$SCRIPT_DIR/common-posix.sh"
if [ ! -f "$COMMON_POSIX_SH" ]; then
    COMMON_POSIX_SH="$SCRIPT_DIR/../../scripts/common-posix.sh"
fi
# shellcheck source=./common-posix.sh
source "$COMMON_POSIX_SH"

cd "$SCRIPT_DIR"

cleanup() {
    rm -f version_check.txt
    if [ -L Bin64 ]; then
        rm -f Bin64
    fi
}
trap cleanup EXIT

SERVER_ROOT="$(detect_server_root 2>/dev/null || true)"
if [ -z "$SERVER_ROOT" ]; then
    fail "Could not detect Space Engineers Dedicated Server install location. Set SE_SERVER_ROOT."
fi
[ -d "$SERVER_ROOT/DedicatedServer64" ] || fail "Missing DedicatedServer64 folder under $SERVER_ROOT."
log "Server Root: $SERVER_ROOT"

log "Verifying Python"
require_python_3_13
log "Verifying git"
require_cmd git
ensure_uv
ensure_uv_sync
ensure_ilspycmd

DATA_ROOT="$(default_data_home)/server-code"
log "Data Root: $DATA_ROOT"
ensure_directory_link "Data" "$DATA_ROOT"
ensure_git_repo "Data"

ensure_temp_link "Bin64" "$SERVER_ROOT/DedicatedServer64"

log "Checking current game version"
set +e
uv run python -u check_version.py Bin64 Data >version_check.txt
RC=$?
set -e
case "$RC" in
    0)
        log "Game version unchanged - keeping existing decompilation"
        ;;
    2)
        log "Game version differs or no previous version recorded - wiping stale outputs"
        rm -rf Data/Decompiled Data/CodeIndex Data/Content
        mkdir -p Data/Decompiled
        ;;
    *)
        cat version_check.txt >&2
        fail "Failed to determine current game version."
        ;;
esac

if [ ! -d Data/Decompiled/VRage.XmlSerializers ]; then
    log "Decompiling the server assemblies"
    ILSPYCMD="$ILSPYCMD" ./Decompile.sh

    log "Recording game version and committing decompiled sources"
    uv run python -u check_version.py --write Bin64 Data
    GAME_VERSION_LABEL="$(uv run python -u check_version.py --print Bin64)"
    [ -n "$GAME_VERSION_LABEL" ] || fail "Could not determine game version label."
    log "Game version: $GAME_VERSION_LABEL"

    git -C Data add -A
    git -C Data \
        -c user.name="se-dev-skills" \
        -c user.email="se-dev-skills@localhost" \
        commit -m "$GAME_VERSION_LABEL" >/dev/null || log "(No commit made: working tree clean or nothing to commit)"
fi

if [ ! -d Data/Content ]; then
    log "Copying indexable content"
    uv run python -u copy_content.py "$SERVER_ROOT/Content"
fi

if [ ! -f Data/CodeIndex/class_declarations.csv ]; then
    log "Indexing decompiled code"
    mkdir -p Data/CodeIndex
    uv run python -OO -u index_code.py Data/Decompiled Data/CodeIndex
fi

if [ ! -f Data/CodeIndex/content_index.csv ]; then
    log "Indexing content files"
    uv run python -u index_content.py Data/Content Data/Decompiled Data/CodeIndex
fi

: >Prepare.DONE
log "DONE"
