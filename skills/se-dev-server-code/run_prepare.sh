#!/bin/bash
# run_prepare.sh - Wrapper to run Prepare.bat correctly from any shell

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo "Running preparation from: $SCRIPT_DIR"

if [ -f "Prepare.DONE" ]; then
    echo "✓ Preparation already complete (Prepare.DONE exists)"
    exit 0
fi

echo "Starting preparation... This may take 5-15 minutes."
echo "---"

# Run Prepare.bat using full path (works from any shell on Windows)
if cmd //c "$SCRIPT_DIR/Prepare.bat" >Prepare.log 2>&1; then
    if [ -f "Prepare.DONE" ]; then
        echo "---"
        echo "✓ Preparation completed successfully"
        echo ""
        echo "You can now use the skill features:"
        echo "  - Run code searches: uv run search_code.py --help"
        echo "  - Test the skill: ./test_search.bat"
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
    echo "✗ Prepare.bat execution failed"
    echo ""
    echo "Check Prepare.log for details:"
    tail -20 Prepare.log
    exit 1
fi
