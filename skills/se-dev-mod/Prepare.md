1. Run `python --version`, if it fails or not at least 3.11 then inform user and stop here.
2. Inform user this is one-time preparation taking about 10 seconds.
3. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux run `./prepare.sh >Prepare.log 2>&1`. Use this same folder as CWD, where `Prepare.md` sits.
4. Preparation successful if last line of `Prepare.log` is `DONE`. If it fails, inform user and stop here.

Notes:
- If Graphify is available, preparation builds or updates a separate graph for the local mod folder.
- If Graphify is missing, preparation prompts to install it because it is highly recommended. Set `SE_DEV_GRAPHIFY=0` to skip.
- Set `SE_DEV_MOD_PROJECT_ROOT` to graph a specific mod project root instead of the local mod folder.
