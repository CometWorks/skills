#!/usr/bin/env bash
#
# Code search smoke test for the decompiled server code index (Linux).
#
# The checks themselves live in test_search_code.py so that Linux and Windows
# run exactly the same assertions. Exits non-zero if any check failed.

set -u
cd "$(dirname "$(readlink -f "$0")")"

uv run test_search_code.py
