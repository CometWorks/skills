"""
Clone or update the MagnetarHub registry under the skill's Data folder.

MagnetarHub is the server-plugin registry loaded by Magnetar (the server-side
counterpart to PluginHub). It uses the same GitHubPlugin XML schema, except the
GitHub repository is named in <RepoId> while <Id> holds a GUID.

The repository is cloned with git so it can be updated cheaply with git pull on
subsequent runs. The clone lives in the skill profile folder (Data/MagnetarHub)
rather than the skill folder itself.

Set SE_MAGNETARHUB_URL to override the registry URL (e.g. a fork or a private
mirror). Set SE_MAGNETARHUB=0 to skip cloning entirely.
"""

import os
import subprocess
import sys
import time

from plugin_paths import DATA_DIR, MAGNETARHUB_DIR

DEFAULT_REPO_URL = "https://github.com/CometWorks/magnetar-hub.git"
REFRESH_INTERVAL_SECONDS = 2 * 3600


def _run_git(args: list, cwd=None) -> int:
    return subprocess.run(["git", *args], cwd=cwd).returncode


def _is_recent(path) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < REFRESH_INTERVAL_SECONDS


def main() -> int:
    if os.environ.get("SE_MAGNETARHUB", "").strip() == "0":
        print("SE_MAGNETARHUB=0 set; skipping MagnetarHub registry.")
        return 0

    repo_url = os.environ.get("SE_MAGNETARHUB_URL", "").strip() or DEFAULT_REPO_URL

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if (MAGNETARHUB_DIR / ".git").exists():
        if _is_recent(MAGNETARHUB_DIR / ".git" / "FETCH_HEAD"):
            print(f"MagnetarHub registry is up to date at {MAGNETARHUB_DIR}.")
            return 0
        print(f"Updating MagnetarHub registry in {MAGNETARHUB_DIR}...")
        rc = _run_git(["pull", "--ff-only"], cwd=MAGNETARHUB_DIR)
        if rc != 0:
            print("git pull failed", file=sys.stderr)
            return rc
        return 0

    print(f"Cloning MagnetarHub registry into {MAGNETARHUB_DIR}...")
    rc = _run_git(["clone", "--depth", "1", repo_url, str(MAGNETARHUB_DIR)])
    if rc != 0:
        print("git clone failed", file=sys.stderr)
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
