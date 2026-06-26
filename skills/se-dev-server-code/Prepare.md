1. Run `python --version`, if it fails or not at least 3.11 then inform user and stop here.
2. Run `git --version`, if it fails inform user that command line `git` client must be available on `PATH` and stop here.
3. Inform user this is one time preparation, takes about 5-15 minutes. Highlight this message.
4. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux run `./prepare.sh >Prepare.log 2>&1`. Use this same folder as CWD, where `Prepare.md` sits.
5. Preparation succeeds if last line of `Prepare.log` is `DONE`. If it fails, inform user and stop here.

Notes:
- If auto-detection fails, set `SE_SERVER_ROOT` before running preparation. May point either to dedicated server root or directly to `DedicatedServer64` directory.
- Actual data (decompiled sources, content files and indexes) stored under `%USERPROFILE%\.se-dev\server-code\` on Windows and `~/.se-dev/server-code/` on Linux, exposed via `Data` junction/symlink in this skill folder.
- Local Git repository inside `Data` folder records every successful decompilation as commit whose message is server version label (e.g. `1.208.015 b4`).
- Subsequent runs detect server updates automatically: if server version changes, previous `Decompiled/`, `Content/` and `CodeIndex/` directories are wiped and rebuilt; previous version stays available in Git history.
- If Graphify is available, preparation builds or updates a separate graph for `Data/Decompiled`.
- If Graphify is missing, preparation prompts to install it because it is highly recommended. Set `SE_DEV_GRAPHIFY=0` to skip.
- Set `SE_DEV_SERVER_CODE_GRAPH_ROOT` to graph a different server-code root.
