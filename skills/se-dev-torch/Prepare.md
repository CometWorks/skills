1. Run `python --version`, stop if missing or older than 3.11.
2. Run `git --version`, stop if command line `git` client missing.
3. Inform user this is one-time preparation, usually takes about 1 minute. The optional Graphify graph is off by default; if the user wants it, run prepare with `SE_DEV_GRAPHIFY=1` set — over the Torch checkout it adds roughly another minute. See [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
4. If user already has Torch checkout, set `TORCH_ROOT` to that repository root before preparation. Must contain `Torch.sln`.
5. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux/macOS run `./Prepare.sh >Prepare.log 2>&1`. `run_prepare.sh` also acceptable as cross-platform wrapper. Use this skill folder as CWD.
6. Preparation successful if last line of `Prepare.log` is `DONE`.

Notes:
- If `TORCH_ROOT` not set, preparation clones or updates `https://github.com/TorchAPI/Torch` under skill's persistent `Data/Sources/Torch` folder.
- Selected source root written to `Data/torch_root.txt`.
- Re-run preparation after changing `TORCH_ROOT` or after updating Torch checkout if you want fresh index.
- The optional Graphify graph is off by default. With `SE_DEV_GRAPHIFY=1` set, preparation builds or updates a separate graph for the selected Torch checkout; if `graphify` is missing it offers to install it. An interrupted/unclustered graph is detected and rebuilt from scratch. Note a Torch checkout is a mixed corpus (has docs) — see the API-key note in [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
- Set `SE_DEV_TORCH_PLUGIN_ROOT` to graph a specific Torch plugin project root instead of the Torch checkout.
