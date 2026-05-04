#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "Running preparation from: $SCRIPT_DIR"

if [ -f "Prepare.DONE" ]; then
    echo "✓ Preparation already complete (Prepare.DONE exists)"
    exit 0
fi

echo "Starting preparation... This may take 5-15 minutes."
echo "---"

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*)
        PREP_CMD=(cmd //c "$SCRIPT_DIR/Prepare.bat")
        ;;
    *)
        PREP_CMD=(bash "$SCRIPT_DIR/Prepare.sh")
        ;;
esac

if "${PREP_CMD[@]}" >Prepare.log 2>&1; then
    if [ -f "Prepare.DONE" ]; then
        echo "---"
        echo "✓ Preparation completed successfully"
        echo ""
        echo "You can now use the skill features:"
        echo "  - Run code searches: uv run search_server_code.py --help"
        echo "  - Test the skill: ./test_search_server_code.bat"
        exit 0
    else
        echo "---"
        echo "✗ Preparation may have failed - Prepare.DONE not found"
        echo ""
        echo "Check Prepare.log for details:"
        tail -20 Prepare.log
        exit 1
    fi
else
    echo "---"
    echo "✗ Preparation failed"
    echo ""
    echo "Check Prepare.log for details:"
    tail -20 Prepare.log
    exit 1
fi
