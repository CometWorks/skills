#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $(basename "$0") <target_skills_folder>" >&2
    exit 1
fi

TARGET="$1"
SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -P -- "$SCRIPT_DIR/../.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

mkdir -p "$TARGET"

skills=(
    se-dev-game-code
    se-dev-mod
    se-dev-plugin
    se-dev-torch
    se-dev-script
    se-dev-server-code
)

success=0
failed=0

echo "Installing Space Engineers Developer Skills"
echo "Source: $SKILLS_DIR"
echo "Target: $TARGET"
echo

for skill in "${skills[@]}"; do
    source_path="$SKILLS_DIR/$skill"
    link_path="$TARGET/$skill"

    if [ ! -d "$source_path" ]; then
        echo "[FAIL] $skill - source folder missing"
        failed=$((failed + 1))
        continue
    fi

    if [ -L "$link_path" ] || [ -e "$link_path" ]; then
        echo "[SKIP] $skill - already exists"
        continue
    fi

    echo "[INSTALL] $skill"
    if ln -s "$source_path" "$link_path"; then
        success=$((success + 1))
    else
        echo "  ERROR: Failed to create symlink"
        failed=$((failed + 1))
    fi
done

echo
echo "Installation complete: $success installed, $failed failed"
if [ "$failed" -gt 0 ]; then
    exit 1
fi
