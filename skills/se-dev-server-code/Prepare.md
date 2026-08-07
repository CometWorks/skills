1. Run `python --version`, if it fails or not at least 3.11 then inform user and stop here.
2. Run `git --version`, if it fails inform user that command line `git` client must be available on `PATH` and stop here.
3. Inform user this is one time preparation. Decompiling and indexing takes about 5-15 minutes. Highlight this message.
   - The Graphify graph builds **automatically** when the fast Rust clustering backend is available (Python 3.12 via `uv`, which prepare provisions in ~30-60s the first time); over the ~10,000 decompiled files clustering then takes ~1-2 minutes (a ~220k-node graph). If that backend cannot be provisioned, prepare falls back to slow single-core clustering (~10-30 minutes) and skips the graph unless you opt in — ask the user before opting into the slow build, then run prepare with `SE_DEV_GRAPHIFY=1` set (e.g. `SE_DEV_GRAPHIFY=1 ./prepare.sh`). `SE_DEV_GRAPHIFY=0` disables the graph entirely. See [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
4. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux run `./prepare.sh >Prepare.log 2>&1`. Use this same folder as CWD, where `Prepare.md` sits.
5. Preparation succeeds if last line of `Prepare.log` is `DONE`. If it fails, inform user and stop here.

Notes:
- If auto-detection fails, set `SE_SERVER_ROOT` before running preparation. May point either to dedicated server root or directly to `DedicatedServer64` directory.
- Actual data (decompiled sources, content files and indexes) stored under `%USERPROFILE%\.se-dev\server-code\` on Windows and `~/.se-dev/server-code/` on Linux, exposed via `Data` junction/symlink in this skill folder.
- Local Git repository inside `Data` folder records every successful decompilation (decompiled sources plus the copied content files) as commit whose message is server version label (e.g. `1.208.015 b4`).
- Subsequent runs detect server updates automatically: if server version changes, previous `Decompiled/` (including the copied `Content/`) and `CodeIndex/` directories are wiped and rebuilt; previous version stays available in Git history.
- The Graphify graph builds automatically with the fast Rust backend, or on opt-in (`SE_DEV_GRAPHIFY=1`) using the slow single-core fallback; `SE_DEV_GRAPHIFY=0` disables it. Preparation builds or updates a separate graph for `Data/Decompiled`; on the slow path, if `graphify` is missing it offers to install it. An interrupted/unclustered graph is detected and rebuilt from scratch. Verify a graph with `bash ../se-dev/graphify-check.sh Data/Decompiled --deep` or run `./test_graphify_server_code.sh`. See [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
- Set `SE_DEV_SERVER_CODE_GRAPH_ROOT` to graph a different server-code root.
