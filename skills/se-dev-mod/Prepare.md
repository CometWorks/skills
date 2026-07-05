1. Run `python --version`, if it fails or not at least 3.11 then inform user and stop here.
2. Inform user this is one-time preparation taking about 10 seconds. The optional Graphify graph is off by default; if the user wants it, run prepare with `SE_DEV_GRAPHIFY=1` set — for local mods it adds only seconds to a couple of minutes. See [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
3. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux run `./prepare.sh >Prepare.log 2>&1`. Use this same folder as CWD, where `Prepare.md` sits.
4. Preparation successful if last line of `Prepare.log` is `DONE`. If it fails, inform user and stop here.

Notes:
- The optional Graphify graph is off by default. With `SE_DEV_GRAPHIFY=1` set, preparation builds or updates a separate graph for the local mod folder; if `graphify` is missing it offers to install it. An interrupted/unclustered graph is detected and rebuilt from scratch.
- Set `SE_DEV_MOD_PROJECT_ROOT` to graph a specific mod project root instead of the local mod folder.
