1. Run `python --version`, if it fails or not at least 3.13 then inform the user and stop here.
2. Run `git --version`, if it fails inform the user that the command line `git` client must be available on `PATH` and stop here.
3. Inform the user that this is a one time preparation which will take about 5-15 minutes. Highlight this message.
4. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux/macOS run `./Prepare.sh >Prepare.log 2>&1`. `run_prepare.sh` is also acceptable as a cross-platform wrapper. Use this same folder as CWD, this is where `Prepare.md` is situated.
5. The preparation is successful if the last line of `Prepare.log` is `DONE`. If it fails, inform the user and stop here.

Notes:
- The actual data (decompiled sources, content files and indexes) is stored under `%USERPROFILE%\.se-dev\game-code\` on Windows and `~/.se-dev/game-code/` on Linux/macOS, exposed via the `Data` junction/symlink in this skill folder.
- A local Git repository inside the `Data` folder records every successful decompilation as a commit whose message is the game version label (e.g. `1.208.015 b4`).
- Subsequent runs detect game updates automatically: if the game's version changes, the previous `Decompiled/`, `Content/` and `CodeIndex/` directories are wiped and rebuilt; the previous version stays available in the Git history.
