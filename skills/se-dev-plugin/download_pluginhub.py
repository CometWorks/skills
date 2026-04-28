"""
Clone or update the PluginHub registry under the skill's Data folder.

The PluginHub repository is cloned with git so it can be updated cheaply with
git pull on subsequent runs. The clone lives in the skill profile folder
(Data/PluginHub) rather than the skill folder itself.
"""

import subprocess
import sys
import time

from plugin_paths import DATA_DIR, PLUGINHUB_DIR

REPO_URL = "https://github.com/StarCpt/PluginHub.git"
REFRESH_INTERVAL_SECONDS = 2 * 3600


def _run_git(args: list, cwd=None) -> int:
    return subprocess.run(["git", *args], cwd=cwd).returncode


def _is_recent(path) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < REFRESH_INTERVAL_SECONDS


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if (PLUGINHUB_DIR / ".git").exists():
        if _is_recent(PLUGINHUB_DIR / ".git" / "FETCH_HEAD"):
            print(f"PluginHub registry is up to date at {PLUGINHUB_DIR}.")
            return 0
        print(f"Updating PluginHub registry in {PLUGINHUB_DIR}...")
        rc = _run_git(["pull", "--ff-only"], cwd=PLUGINHUB_DIR)
        if rc != 0:
            print("git pull failed", file=sys.stderr)
            return rc
        return 0

    print(f"Cloning PluginHub registry into {PLUGINHUB_DIR}...")
    rc = _run_git(["clone", "--depth", "1", REPO_URL, str(PLUGINHUB_DIR)])
    if rc != 0:
        print("git clone failed", file=sys.stderr)
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
