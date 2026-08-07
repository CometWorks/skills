#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common-posix.sh
source "$SCRIPT_DIR/common-posix.sh"
# shellcheck source=../se-dev/graphify-prepare.sh
source "$SCRIPT_DIR/../se-dev/graphify-prepare.sh"

cd "$SCRIPT_DIR"

cleanup() {
    rm -f version_check.txt
    if [ -L Bin64 ]; then
        rm -f Bin64
    fi
}
trap cleanup EXIT

GAME_ROOT="$(detect_game_root 2>/dev/null || true)"
if [ -z "$GAME_ROOT" ]; then
    fail "Could not detect Space Engineers install location. Set SE_GAME_ROOT."
fi
[ -d "$GAME_ROOT/Bin64" ] || fail "Missing Bin64 folder under $GAME_ROOT."
log "Game Root: $GAME_ROOT"

log "Verifying Python"
require_python_3_11
log "Verifying git"
require_cmd git
ensure_uv
ensure_uv_sync
ensure_ilspycmd

DATA_ROOT="$(default_data_home)/game-code"
log "Data Root: $DATA_ROOT"
ensure_directory_link "Data" "$DATA_ROOT"
ensure_git_repo "Data"

ensure_temp_link "Bin64" "$GAME_ROOT/Bin64"

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
        # Data files are incomplete until preparation finishes for the new game version
        rm -f Prepare.DONE
        rm -rf Data/Decompiled Data/CodeIndex Data/Content Data/graphify-out
        mkdir -p Data/Decompiled
        ;;
    *)
        cat version_check.txt >&2
        fail "Failed to determine current game version."
        ;;
esac

NEED_COMMIT=0

# Bring the Data folder up to the current layout before anything reads it.
# Decompiled holds only decompiled C# code; Content and graphify-out sit beside
# it. Earlier versions of this skill kept both inside Decompiled.
if [ -d Data/Decompiled/Content ]; then
    log "Moving Data/Decompiled/Content up to Data/Content"
    rm -rf Data/Content
    mv Data/Decompiled/Content Data/Content
    NEED_COMMIT=1
fi
if [ -d Data/Decompiled/graphify-out ]; then
    if [ -d Data/graphify-out ]; then
        rm -rf Data/Decompiled/graphify-out
    else
        log "Moving Data/Decompiled/graphify-out up to Data/graphify-out"
        mv Data/Decompiled/graphify-out Data/graphify-out
    fi
fi

# Content is versioned, so it must not be ignored (older installs ignored it).
if grep -qxF 'Content/' Data/.gitignore 2>/dev/null; then
    grep -vxF 'Content/' Data/.gitignore >Data/.gitignore.tmp
    mv Data/.gitignore.tmp Data/.gitignore
    NEED_COMMIT=1
fi
# The Graphify graph is a large regenerable artifact, so it must be ignored.
# This has to be in place before the commit below, which stages everything.
if ! grep -qxF 'graphify-out/' Data/.gitignore 2>/dev/null; then
    echo 'graphify-out/' >>Data/.gitignore
    NEED_COMMIT=1
fi

if [ ! -d Data/Decompiled/VRage.XmlSerializers ]; then
    log "Decompiling the game assemblies"
    ILSPYCMD="$ILSPYCMD" ./Decompile.sh

    log "Fixing case-collision folders (Gui vs GUI, Filesystem vs FileSystem)"
    uv run python -u fix_case_collisions.py Data/Decompiled
    NEED_COMMIT=1
fi

# Only the indexable text files are copied (no binaries), so the definition
# files can be versioned and their changes reviewed.
if [ ! -d Data/Content ]; then
    log "Copying indexable content"
    uv run python -u copy_content.py "$GAME_ROOT/Content"
    NEED_COMMIT=1
fi

if [ "$NEED_COMMIT" = 1 ]; then
    log "Recording game version and committing decompiled sources and content"
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

if [ ! -f Data/CodeIndex/class_declarations.csv ]; then
    log "Indexing decompiled code"
    mkdir -p Data/CodeIndex
    uv run python -OO -u index_code.py Data/Decompiled Data/CodeIndex
fi

if [ ! -f Data/CodeIndex/content_index.csv ]; then
    log "Indexing content files"
    uv run python -u index_content.py Data/Content Data/Decompiled Data/CodeIndex
fi

# Only the decompiled C# code is graphed; the graph itself is written beside it
# (Data/graphify-out) so it never pollutes the graphed tree or the repository.
GAME_CODE_GRAPH_ROOT="${SE_DEV_GAME_CODE_GRAPH_ROOT:-Data/Decompiled}"
GAME_CODE_GRAPH_OUT="${SE_DEV_GAME_CODE_GRAPH_OUT:-Data}"
se_dev_graphify_prepare "se-dev-game-code" "$GAME_CODE_GRAPH_ROOT" "$GAME_CODE_GRAPH_OUT"

: >Prepare.DONE
log "DONE"
