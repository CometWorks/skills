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


def _git_output(args: list, cwd=None) -> str:
    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _is_recent(path) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) < REFRESH_INTERVAL_SECONDS


def _is_up_to_date(repo) -> bool:
    """Whether the checked out tree is current, not just recently fetched.

    git pull writes FETCH_HEAD during the fetch phase even when the merge that
    follows aborts (local modifications, diverged history), so the FETCH_HEAD
    timestamp alone reports a stale clone as fresh. Also require HEAD to match
    the remote-tracking branch that the last fetch updated.
    """
    if not _is_recent(repo / ".git" / "FETCH_HEAD"):
        return False
    head = _git_output(["rev-parse", "HEAD"], cwd=repo)
    upstream = _git_output(["rev-parse", "@{u}"], cwd=repo)
    return bool(head) and head == upstream


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if (PLUGINHUB_DIR / ".git").exists():
        if _is_up_to_date(PLUGINHUB_DIR):
            print(f"PluginHub registry is up to date at {PLUGINHUB_DIR}.")
            return 0
        print(f"Updating PluginHub registry in {PLUGINHUB_DIR}...")
        rc = _run_git(["pull", "--ff-only"], cwd=PLUGINHUB_DIR)
        if rc != 0:
            print("git pull failed", file=sys.stderr)
            dirty = _git_output(["status", "--porcelain"], cwd=PLUGINHUB_DIR)
            if dirty:
                print(
                    f"{PLUGINHUB_DIR} has local modifications blocking the "
                    "fast-forward. Revert them or delete the clone "
                    "to force a fresh download:",
                    file=sys.stderr,
                )
                print(dirty, file=sys.stderr)
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
