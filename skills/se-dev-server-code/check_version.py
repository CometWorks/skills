#!/usr/bin/env python3
"""
Detect the current Space Engineers Dedicated Server game version from the
server binaries.

Decompiles only the SpaceEngineersGame type from SpaceEngineers.Game.dll using
ilspycmd, then reads the SE_VERSION, CLIENT_BUILD_NUMBER and SERVER_BUILD_NUMBER
constants to derive a human-readable label like "1.208.015 b4".

Modes:
    check_version.py <Bin64> <Data>
        Compare the current game version with the one previously recorded in
        <Data>/game_version.txt. Exit codes:
            0 = versions match
            2 = version differs or no recorded version
            1 = error while determining the version

    check_version.py --print <Bin64>
        Print the current version label only.

    check_version.py --write <Bin64> <Data>
        Write the current version into <Data>/game_version.txt and print the
        version label.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


VERSION_FILE_NAME = "game_version.txt"
GAME_DLL = "SpaceEngineers.Game.dll"
GAME_TYPE = "SpaceEngineers.Game.SpaceEngineersGame"


def _resolve_ilspycmd() -> str:
    env_override = os.environ.get("ILSPYCMD", "").strip()
    if env_override:
        return env_override

    from_path = shutil.which("ilspycmd")
    if from_path:
        return from_path

    local_tool = Path.home() / ".se-dev" / "tools" / "ilspycmd" / "ilspycmd"
    if local_tool.is_file():
        return str(local_tool)

    raise FileNotFoundError(
        "ilspycmd not found. Run Prepare.bat/prepare.sh first or set ILSPYCMD."
    )


def _format_label(se_version: int, client_build: int) -> str:
    major = se_version // 1000000
    minor = (se_version // 1000) % 1000
    patch = se_version % 1000
    return f"{major}.{minor:03d}.{patch:03d} b{client_build}"


def _decompile_type(bin64: Path) -> str:
    dll = bin64 / GAME_DLL
    if not dll.is_file():
        raise FileNotFoundError(f"Game DLL not found: {dll}")

    tmp_dir = Path(tempfile.mkdtemp(prefix="se_version_"))
    try:
        # ilspycmd writes the decompiled type into the output directory
        cmd = [
            _resolve_ilspycmd(),
            "-t", GAME_TYPE,
            "--disable-updatecheck",
            "-o", str(tmp_dir),
            str(dll),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"ilspycmd failed (exit {result.returncode}):\n"
                f"stdout:\n{result.stdout}\n"
                f"stderr:\n{result.stderr}"
            )

        # Concatenate any produced .cs files (usually a single SpaceEngineersGame.cs)
        text_chunks = []
        for cs_file in tmp_dir.rglob("*.cs"):
            text_chunks.append(cs_file.read_text(encoding="utf-8", errors="replace"))

        if not text_chunks:
            # Some ilspycmd builds print to stdout instead
            if result.stdout:
                text_chunks.append(result.stdout)

        if not text_chunks:
            raise RuntimeError("ilspycmd produced no output for SpaceEngineersGame")

        return "\n".join(text_chunks)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _extract_constants(source: str) -> dict:
    fields = {}
    for name in ("SE_VERSION", "CLIENT_BUILD_NUMBER", "SERVER_BUILD_NUMBER"):
        match = re.search(
            rf"public\s+const\s+int\s+{name}\s*=\s*(\d+)\s*;",
            source,
        )
        if not match:
            raise RuntimeError(f"Could not find {name} in decompiled SpaceEngineersGame")
        fields[name] = int(match.group(1))
    return fields


def _read_current(bin64: Path) -> dict:
    source = _decompile_type(bin64)
    return _extract_constants(source)


def _format_file_contents(fields: dict) -> str:
    return (
        f"SE_VERSION={fields['SE_VERSION']}\n"
        f"CLIENT_BUILD_NUMBER={fields['CLIENT_BUILD_NUMBER']}\n"
        f"SERVER_BUILD_NUMBER={fields['SERVER_BUILD_NUMBER']}\n"
    )


def _read_recorded(version_file: Path) -> dict:
    if not version_file.is_file():
        return {}
    fields = {}
    for line in version_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        name, _, value = line.partition("=")
        try:
            fields[name.strip()] = int(value.strip())
        except ValueError:
            pass
    return fields


def _cmd_check(bin64: Path, data_dir: Path) -> int:
    try:
        current = _read_current(bin64)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    version_file = data_dir / VERSION_FILE_NAME
    recorded = _read_recorded(version_file)
    label = _format_label(current["SE_VERSION"], current["CLIENT_BUILD_NUMBER"])

    if not recorded:
        print(f"MISSING (current: {label})")
        return 2

    if recorded == current:
        print(f"MATCH ({label})")
        return 0

    prev_label = ""
    if "SE_VERSION" in recorded and "CLIENT_BUILD_NUMBER" in recorded:
        prev_label = _format_label(
            recorded["SE_VERSION"], recorded["CLIENT_BUILD_NUMBER"]
        )
    print(f"DIFFER (recorded: {prev_label}, current: {label})")
    return 2


def _cmd_print(bin64: Path) -> int:
    try:
        current = _read_current(bin64)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(_format_label(current["SE_VERSION"], current["CLIENT_BUILD_NUMBER"]))
    return 0


def _cmd_write(bin64: Path, data_dir: Path) -> int:
    try:
        current = _read_current(bin64)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    data_dir.mkdir(parents=True, exist_ok=True)
    version_file = data_dir / VERSION_FILE_NAME
    version_file.write_text(_format_file_contents(current), encoding="utf-8")
    label = _format_label(current["SE_VERSION"], current["CLIENT_BUILD_NUMBER"])
    print(label)
    return 0


def main(argv):
    args = list(argv[1:])
    if not args:
        print(__doc__)
        return 1

    if args[0] == "--print":
        if len(args) != 2:
            print("Usage: check_version.py --print <Bin64>", file=sys.stderr)
            return 1
        return _cmd_print(Path(args[1]))

    if args[0] == "--write":
        if len(args) != 3:
            print("Usage: check_version.py --write <Bin64> <Data>", file=sys.stderr)
            return 1
        return _cmd_write(Path(args[1]), Path(args[2]))

    if len(args) != 2:
        print("Usage: check_version.py <Bin64> <Data>", file=sys.stderr)
        return 1
    return _cmd_check(Path(args[0]), Path(args[1]))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
