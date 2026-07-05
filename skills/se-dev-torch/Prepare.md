1. Run `python --version`, stop if missing or older than 3.11.
2. Run `git --version`, stop if command line `git` client missing.
3. Inform user this is one-time preparation, usually takes about 1 minute. The Graphify graph builds automatically when the fast Rust clustering backend is available (Python 3.12 via `uv`, provisioned automatically); over the Torch checkout it adds roughly another minute either way. Without that backend it stays opt-in (`SE_DEV_GRAPHIFY=1`); `SE_DEV_GRAPHIFY=0` disables it. See [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
4. If user already has Torch checkout, set `TORCH_ROOT` to that repository root before preparation. Must contain `Torch.sln`.
5. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux/macOS run `./Prepare.sh >Prepare.log 2>&1`. `run_prepare.sh` also acceptable as cross-platform wrapper. Use this skill folder as CWD.
6. Preparation successful if last line of `Prepare.log` is `DONE`.

Notes:
- If `TORCH_ROOT` not set, preparation clones or updates `https://github.com/TorchAPI/Torch` under skill's persistent `Data/Sources/Torch` folder.
- Selected source root written to `Data/torch_root.txt`.
- Re-run preparation after changing `TORCH_ROOT` or after updating Torch checkout if you want fresh index.
- The Graphify graph builds automatically with the fast Rust backend, or on opt-in (`SE_DEV_GRAPHIFY=1`) using the slow single-core fallback; `SE_DEV_GRAPHIFY=0` disables it. Preparation builds or updates a separate graph for the selected Torch checkout; on the slow path, if `graphify` is missing it offers to install it. An interrupted/unclustered graph is detected and rebuilt from scratch. Note a Torch checkout is a mixed corpus (has docs) — see the API-key note in [Prepare-time Graphify graphs](../se-dev/GraphifyPrepare.md).
- Set `SE_DEV_TORCH_PLUGIN_ROOT` to graph a specific Torch plugin project root instead of the Torch checkout.
