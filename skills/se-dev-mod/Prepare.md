1. Run `python --version`, if it fails or not at least 3.11 then inform user and stop here.
2. Inform user this is one-time preparation taking about 10 seconds. The Graphify graph builds automatically when the fast Rust clustering backend is available (Python 3.12 via `uv`, provisioned automatically); for local mods it adds only seconds to a couple of minutes either way. Without that backend it stays opt-in (`SE_DEV_GRAPHIFY=1`); `SE_DEV_GRAPHIFY=0` disables it. See [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
3. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux run `./prepare.sh >Prepare.log 2>&1`. Use this same folder as CWD, where `Prepare.md` sits.
4. Preparation successful if last line of `Prepare.log` is `DONE`. If it fails, inform user and stop here.

Notes:
- The Graphify graph builds automatically with the fast Rust backend, or on opt-in (`SE_DEV_GRAPHIFY=1`) using the slow single-core fallback; `SE_DEV_GRAPHIFY=0` disables it. Preparation builds or updates a separate graph for the local mod folder; on the slow path, if `graphify` is missing it offers to install it. An interrupted/unclustered graph is detected and rebuilt from scratch.
- Set `SE_DEV_MOD_PROJECT_ROOT` to graph a specific mod project root instead of the local mod folder.
