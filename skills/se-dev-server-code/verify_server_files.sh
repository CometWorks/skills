#!/usr/bin/env bash
# verify_server_files.sh - verify the installed Space Engineers Dedicated Server
# files against the SHA256 digests recorded in Data/server_files.json. POSIX
# (Linux) counterpart of VerifyServerFiles.bat.
#
# Exit codes:
#   0 = every server file matches the recorded hashes
#   1 = error (server install or hash file not found)
#   2 = files are missing, modified or extra
#
# Extra arguments are passed through to hash_server_files.py (e.g. -j 8, -q).

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common-posix.sh
source "$SCRIPT_DIR/common-posix.sh"

cd "$SCRIPT_DIR"

SERVER_ROOT="$(detect_server_root 2>/dev/null || true)"
if [ -z "$SERVER_ROOT" ]; then
    fail "Could not detect the Space Engineers Dedicated Server install location.
Set the SE_SERVER_ROOT environment variable to the server's root folder
(the folder containing DedicatedServer64, Content, etc.)."
fi
log "Server Root: $SERVER_ROOT"

[ -f Data/server_files.json ] || fail "No recorded hashes in Data/server_files.json. Run ./prepare.sh first."

ensure_uv
exec uv run python -u hash_server_files.py --verify "$SERVER_ROOT" Data "$@"
