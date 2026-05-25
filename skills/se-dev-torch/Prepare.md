1. Run `python --version`, and stop if it is missing or older than 3.11.
2. Run `git --version`, and stop if the command line `git` client is missing.
3. Inform the user that this is a one-time preparation which usually takes about 1 minute.
4. If the user already has a Torch checkout, set `TORCH_ROOT` to that repository root before preparation. It must contain `Torch.sln`.
5. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux/macOS run `./Prepare.sh >Prepare.log 2>&1`. `run_prepare.sh` is also acceptable as a cross-platform wrapper. Use this skill folder as CWD.
6. Preparation is successful if the last line of `Prepare.log` is `DONE`.

Notes:
- If `TORCH_ROOT` is not set, preparation clones or updates `https://github.com/TorchAPI/Torch` under the skill's persistent `Data/Sources/Torch` folder.
- The selected source root is written to `Data/torch_root.txt`.
- Re-run preparation after changing `TORCH_ROOT` or after updating the Torch checkout if you want a fresh index.
