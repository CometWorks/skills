#!/usr/bin/env bash
# verify_game_files.sh - verify the installed Space Engineers files against the
# SHA256 digests recorded in Data/game_files.json. POSIX (Linux) counterpart of
# VerifyGameFiles.bat.
#
# Exit codes:
#   0 = every game file matches the recorded hashes
#   1 = error (game install or hash file not found)
#   2 = files are missing, modified or extra
#
# Extra arguments are passed through to hash_game_files.py (e.g. -j 8, -q).

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common-posix.sh
source "$SCRIPT_DIR/common-posix.sh"

cd "$SCRIPT_DIR"

GAME_ROOT="$(detect_game_root 2>/dev/null || true)"
if [ -z "$GAME_ROOT" ]; then
    fail "Could not detect the Space Engineers install location.
Set the SE_GAME_ROOT environment variable to the game's root folder
(the folder containing Bin64, Content, etc.)."
fi
log "Game Root: $GAME_ROOT"

[ -f Data/game_files.json ] || fail "No recorded hashes in Data/game_files.json. Run ./prepare.sh first."

ensure_uv
exec uv run python -u hash_game_files.py --verify "$GAME_ROOT" Data "$@"
