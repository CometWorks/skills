#!/usr/bin/env bash
# clean.sh - removes everything that prepare.sh creates inside the skill
# folder. The Data folder (a symlink to ~/.se-dev/server-code) is
# preserved: only the symlink itself is removed so the actual contents
# (Decompiled, CodeIndex, Content, .git) survive across runs.
set -u
cd "$(dirname "$(readlink -f "$0")")"

# Remove the Data symlink (NOT its contents - plain rm on a symlink removes
# only the link and leaves the target folder intact). If Data happens to be
# a real directory, rm without -r will refuse, which preserves user data.
[ -L Data ] && rm Data

# Remove the Bin64 symlink (also leaves the actual server install untouched).
[ -L Bin64 ] && rm Bin64

# Remove transient skill artefacts.
rm -rf __pycache__
rm -rf .venv
rm -f busybox.exe
rm -f Decompile.log
rm -f Prepare.log
rm -f Prepare.DONE
rm -f version_check.txt

exit 0
