#!/usr/bin/env bash
# clean.sh - removes everything that prepare.sh creates inside the skill
# folder. The Data folder (a symlink to ~/.se-dev/script) is preserved:
# only the symlink itself is removed so the actual contents
# (CodeIndex, scripts.json, script_hashes.json) survive across runs.
set -u
cd "$(dirname "$(readlink -f "$0")")"

[ -L Data ]         && rm Data
[ -L LocalScripts ] && rm LocalScripts

rm -rf __pycache__
rm -rf .venv
rm -f busybox.exe
rm -f Prepare.log
rm -f Prepare.DONE

exit 0
