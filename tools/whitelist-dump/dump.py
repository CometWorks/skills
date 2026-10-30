"""Dumps the PB and mod API whitelists of the installed game with a headless, offline Pulsar client.

    python3 dump.py --pulsar <Pulsar folder> --appdata <game data folder> --out <folder>
                    [--bin64 DIR] [--client-id ID] [--timeout SECONDS]

--pulsar   a Pulsar working folder of its own, not the one you play with: its local plugins and
           profile are overwritten to load only the dump plugin in this folder. Copy one with
           new-pulsar-instance.sh from the CometWorks workspace, or copy ~/.config/Pulsar by hand.
--appdata  the game's user data folder for this run, so the client leaves your own alone.
--bin64    the game's Bin64 folder, when Pulsar can't find it through Steam.
--out      where the plugin writes PBApiWhitelist.txt, ModApiWhitelist.txt, PBApiBlacklist.txt
           and game-version.txt.

The client stops at the main menu: the plugin writes the files on the first frame that has the
whitelist, then exits the game. Prints the version and key counts.

On Windows it runs Pulsar Legacy, the .NET Framework game players use, and that dump is the one
the skills ship. On Linux it runs Pulsar Interim headless and offline: the game's whitelist rules
are the same there, but the keys come out in .NET 10 form (System.Private.CoreLib instead of
mscorlib, other System.Linq internals, newer System members), so use it to check whether the
rules changed, not as the shipped file.
"""

import argparse
import os
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
WINDOWS = sys.platform == "win32"
FLAVOR = "Legacy" if WINDOWS else "Interim"


def write_config(pulsar: Path) -> None:
    config = pulsar / FLAVOR
    # Keep the hub sources: the core plugins (dotnet-compat, linux-compat) come from them
    sources = config / "Sources/sources.xml"
    tree = ET.parse(sources)
    local = tree.getroot().find("LocalPluginSources")
    if local is not None:
        tree.getroot().remove(local)
    local = ET.SubElement(tree.getroot(), "LocalPluginSources")
    plugin = ET.SubElement(local, "LocalPlugin")
    for tag, value in (
        ("Name", "whitelist-dump"),
        ("Folder", str(HERE)),
        ("File", "WhitelistDump.xml"),
        ("Enabled", "true"),
    ):
        ET.SubElement(plugin, tag).text = value
    tree.write(sources, encoding="utf-8", xml_declaration=True)
    (config / "Profiles/Current.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<Profile xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
        "<Name>Current</Name><GitHub /><DevFolder><LocalFolderConfig><Id>whitelist-dump</Id>"
        "<DebugBuild>false</DebugBuild></LocalFolderConfig></DevFolder><Local /><Mods /></Profile>\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pulsar", type=Path, required=True)
    ap.add_argument("--appdata", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--bin64", type=Path)
    ap.add_argument("--client-id")
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    pulsar, out = args.pulsar.resolve(), args.out.resolve()
    write_config(pulsar)
    out.mkdir(parents=True, exist_ok=True)
    (out / "game-version.txt").unlink(missing_ok=True)
    args.appdata.mkdir(parents=True, exist_ok=True)

    command = [
        str(pulsar / ("Legacy.exe" if WINDOWS else "Interim.bin")),
        "-noprompt", "-noupdate", "-nosplash", "-sources", "-multiInstance", "-lazySteam",
        "-appdata", str(args.appdata.resolve()),
    ]  # fmt: skip
    if not WINDOWS:
        command += ["--no-steam", "--headless", "--no-render", "--quality", "minimal", "--resolution", "640x480"]
    if args.bin64:
        command += ["-bin64", str(args.bin64.resolve())]
    if args.client_id:
        command += ["--client-id", args.client_id]
    env = {**os.environ, "WHITELIST_DUMP_DIR": str(out), "PULSAR_NO_RENDER": "true"}
    with open(out / "client.log", "w") as log:
        process = subprocess.Popen(
            command, cwd=pulsar, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=not WINDOWS
        )
    deadline = time.monotonic() + args.timeout
    while process.poll() is None and time.monotonic() < deadline:
        if (out / "game-version.txt").exists():
            break
        time.sleep(5)
    # Give the game a moment to exit by itself, then stop what is left of this run only
    try:
        process.wait(60)
    except subprocess.TimeoutExpired:
        if WINDOWS:
            process.kill()
        else:
            os.killpg(process.pid, signal.SIGTERM)
        process.wait(30)

    if not (out / "game-version.txt").exists():
        print(f"FAIL: no whitelist written; see {out / 'client.log'} and the game log in {args.appdata}")
        return 1
    version = (out / "game-version.txt").read_text().strip()
    counts = {
        name: len((out / name).read_text().splitlines()) for name in ("PBApiWhitelist.txt", "ModApiWhitelist.txt")
    }
    print(f"OK: game {version}, " + ", ".join(f"{n} {c} keys" for n, c in counts.items()) + f", in {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
