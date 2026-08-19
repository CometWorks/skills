#!/usr/bin/env python3
"""
Hash every original Space Engineers game file and record the digests.

The result is a plain JSON object mapping each file's path (relative to the
game's install root, forward slashes on every platform) to the lower-case hex
SHA256 of its contents, sorted alphabetically by path and written with 2-space
indentation and LF line endings on every platform, so every pair lands on its
own line. That makes the file diffable: comparing two game versions of it shows
exactly which binaries changed, including the ones that are neither assemblies
nor copied into Data/Content.

The file lives in the skill's Data folder (~/.se-dev/game-code), which is a
local Git repository, so each game version's hashes are committed alongside the
decompiled sources under the version label.

Modes:
    hash_game_files.py --write <GameRoot> <Data>
        Hash the game files and write <Data>/game_files.json.

    hash_game_files.py --verify <GameRoot> <Data>
        Re-hash the game files and compare them with <Data>/game_files.json.
        Exit codes:
            0 = every file matches the recorded hashes
            2 = files are missing, extra or modified
            1 = error (game root or hash file unusable)

Options:
    -j, --jobs N   Number of hashing threads (default: CPU count, max 16).
    -q, --quiet    Suppress progress reporting.

The game root is the folder holding Bin64, Content, etc. - not the Bin64
folder itself.
"""

import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HASH_FILE_NAME = "game_files.json"
HASH_ALGORITHM = "sha256"

# Marker subfolders that identify a folder as the game's root.
GAME_ROOT_MARKERS = ("Bin64", "Content")

# Progress is reported every time this many percent of the total bytes are hashed.
PROGRESS_STEP_PERCENT = 5


def iter_game_files(game_root: Path):
    """Yield (relative_path, absolute_path) for every regular file under the game root.

    Relative paths always use forward slashes so the JSON is identical on
    Windows and Linux. Symlinks and junctions are not followed: only the files
    physically inside the install are hashed.
    """
    for dir_path, dir_names, file_names in os.walk(game_root, followlinks=False):
        dir_names.sort()
        directory = Path(dir_path)
        for file_name in sorted(file_names):
            path = directory / file_name
            # Skip symlinks and anything that is not a regular file (sockets,
            # FIFOs on Linux, dangling reparse points on Windows).
            if path.is_symlink() or not path.is_file():
                continue
            yield path.relative_to(game_root).as_posix(), path


def file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except OSError:
        return 0


def hash_file(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.file_digest(f, HASH_ALGORITHM).hexdigest()


def hash_game_files(game_root: Path, jobs: int, quiet: bool) -> dict:
    """Return {relative_path: sha256} for every file under the game root."""
    entries = list(iter_game_files(game_root))
    sizes = [file_size(path) for _, path in entries]
    total_bytes = sum(sizes)

    if not quiet:
        print(f"Hashing {len(entries)} files ({total_bytes / (1024 ** 3):.1f} GiB) "
              f"using {jobs} threads")

    done_bytes = 0
    reported_percent = 0
    hashes = {}
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        # hashlib releases the GIL while digesting, so the threads overlap
        # reading and hashing. Results arrive in submission (sorted) order.
        digests = pool.map(hash_file, [path for _, path in entries])
        for (rel_path, _), size, digest in zip(entries, sizes, digests):
            hashes[rel_path] = digest
            done_bytes += size
            if quiet or not total_bytes:
                continue
            # Integer percentages: a single huge file can cross several steps at
            # once, and we must not drift past the final 100% report.
            percent = done_bytes * 100 // total_bytes
            if percent >= reported_percent + PROGRESS_STEP_PERCENT:
                reported_percent = percent - percent % PROGRESS_STEP_PERCENT
                print(f"  {percent}% ({len(hashes)}/{len(entries)} files)")

    return hashes


def format_hash_file(hashes: dict) -> str:
    # sort_keys puts the pairs in alphabetical path order, indent=2 puts each
    # pair on its own line. Both are required for a readable diff.
    return json.dumps(hashes, indent=2, sort_keys=True) + "\n"


def load_hash_file(hash_file: Path) -> dict:
    if not hash_file.is_file():
        raise FileNotFoundError(
            f"No recorded hashes: {hash_file}\n"
            f"Run the preparation script to create it."
        )
    return json.loads(hash_file.read_text(encoding="utf-8"))


def resolve_game_root(game_root: Path) -> Path:
    if not game_root.is_dir():
        raise NotADirectoryError(f"Game root does not exist: {game_root}")
    # A common mistake is passing the Bin64 folder (which the decompiler uses)
    # instead of the install root the hashed paths are relative to.
    if not any((game_root / marker).is_dir() for marker in GAME_ROOT_MARKERS):
        raise NotADirectoryError(
            f"Not a Space Engineers install root (no {' or '.join(GAME_ROOT_MARKERS)} "
            f"folder inside): {game_root}"
        )
    return game_root


def cmd_write(game_root: Path, data_dir: Path, jobs: int, quiet: bool) -> int:
    hashes = hash_game_files(resolve_game_root(game_root), jobs, quiet)
    data_dir.mkdir(parents=True, exist_ok=True)
    hash_file = data_dir / HASH_FILE_NAME
    # newline="\n" keeps the file byte-identical on Windows and Linux; the
    # default would translate to CRLF on Windows and spoil cross-machine diffs.
    hash_file.write_text(format_hash_file(hashes), encoding="utf-8", newline="\n")
    print(f"Recorded {len(hashes)} file hashes in {hash_file}")
    return 0


def cmd_verify(game_root: Path, data_dir: Path, jobs: int, quiet: bool) -> int:
    recorded = load_hash_file(data_dir / HASH_FILE_NAME)
    current = hash_game_files(resolve_game_root(game_root), jobs, quiet)

    missing = sorted(set(recorded) - set(current))
    extra = sorted(set(current) - set(recorded))
    modified = sorted(p for p in set(recorded) & set(current) if recorded[p] != current[p])

    for rel_path in missing:
        print(f"MISSING:  {rel_path}")
    for rel_path in modified:
        print(f"MODIFIED: {rel_path}")
    for rel_path in extra:
        print(f"EXTRA:    {rel_path}")

    unchanged = len(current) - len(extra) - len(modified)
    print(f"{unchanged} unchanged, {len(modified)} modified, "
          f"{len(missing)} missing, {len(extra)} extra")

    if missing or extra or modified:
        print("VERIFICATION FAILED")
        return 2

    print("VERIFICATION PASSED")
    return 0


def main(argv):
    args = list(argv[1:])
    jobs = min(16, os.cpu_count() or 4)
    quiet = False

    positional = []
    mode = ""
    while args:
        arg = args.pop(0)
        if arg in ("--write", "--verify"):
            mode = arg
        elif arg in ("-j", "--jobs"):
            if not args:
                print("ERROR: -j/--jobs needs a value", file=sys.stderr)
                return 1
            jobs = max(1, int(args.pop(0)))
        elif arg in ("-q", "--quiet"):
            quiet = True
        elif arg in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            positional.append(arg)

    if not mode or len(positional) != 2:
        print(__doc__, file=sys.stderr)
        return 1

    game_root, data_dir = Path(positional[0]), Path(positional[1])
    try:
        if mode == "--write":
            return cmd_write(game_root, data_dir, jobs, quiet)
        return cmd_verify(game_root, data_dir, jobs, quiet)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
