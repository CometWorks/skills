1. Run `python --version`, if it fails or not at least 3.11 then inform user and stop here.
2. Inform user this is one time preparation taking about 1 minute. The optional Graphify graph is off by default; if the user wants it, run prepare with `SE_DEV_GRAPHIFY=1` set — over the downloaded sources it adds a few seconds up to about a minute. See [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
3. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux run `./prepare.sh >Prepare.log 2>&1`. Use this same folder as CWD, where `Prepare.md` situated.
4. Preparation successful if last line of `Prepare.log` is `DONE`. If it fails, inform user and stop here.

Notes:
- The optional Graphify graph is off by default. With `SE_DEV_GRAPHIFY=1` set, preparation builds or updates a separate graph for downloaded plugin sources under `Data/Sources`; if `graphify` is missing it offers to install it. An interrupted/unclustered graph is detected and rebuilt from scratch.
- Set `SE_DEV_PLUGIN_PROJECT_ROOT` to graph a specific plugin solution/repository root instead of `Data/Sources`.
