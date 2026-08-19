# Server File Hashes

> **Part of the se-dev-server-code skill.** Read this only when you need to know
> *which server files* changed between two builds, or to check an install for
> modified/missing files.

Preparation records a SHA256 digest of **every** file in the Space Engineers
Dedicated Server install into `Data/server_files.json`. Unlike `Data/Decompiled`
(C# code only) and `Data/Content` (text content only), this covers the whole
install: native DLLs, packed assets, models, textures, audio, the
redistributables — everything.

## File format

A plain JSON object, nothing else:

```json
{
  "DedicatedServer64/SpaceEngineersDedicated.exe": "a12e4003b0eaaaf2a66beaa0ff4e8c1269ade48b40c5092ec8928509637da348",
  "DedicatedServer64/Sandbox.Game.dll": "16286813b393b5684fc2b84d12647577763f08939a6eb03de238313d7f45572e",
  "Content/Data/CubeBlocks/CubeBlocks_Armor.sbc": "17f165d5a5ba695f27c023a83aa2b3463e23810e360b7517127e90161eebabda"
}
```

- **Key** — file's path relative to the server's install root (the folder holding
  `DedicatedServer64`, `Content`, etc.), always with forward slashes so the file is
  byte-identical on Windows and Linux.
- **Value** — lower-case hex SHA256 of the file's contents, with no algorithm prefix.
- Keys sorted alphabetically and file written with 2-space indentation, so every pair
  sits on its own line and `git diff` shows one line per changed file.
- Line endings always LF, so the file is byte-identical on Windows and Linux and
  snapshots taken on different machines compare directly.
- Symlinks, junctions and non-regular files skipped; only real files hashed.

## Versioning and diffing

`Data/server_files.json` is committed to the `Data` Git repository along with the
decompiled sources and content, under the game version label. Preparation
regenerates it whenever the game version changes (the wipe step deletes it), so
history has one snapshot per server build.

To see exactly which binaries a server update touched:

```bash
git -C Data log --oneline -- server_files.json   # one commit per game version
git -C Data diff <older-version> <newer-version> -- server_files.json
```

Removed lines with no matching added line are deleted files; added lines with no
matching removed line are new files; a `-`/`+` pair on the same path is a changed
file. This is the only way to spot changes in assets that are neither assemblies
(so not in `Data/Decompiled`) nor text (so not in `Data/Content`) — for example a
repacked model archive or an updated native library.

## Verifying an install

Re-hash the installed server and compare it against the recorded digests:

```bash
# Linux
./verify_server_files.sh
```

```cmd
REM Windows
.\VerifyServerFiles.bat
```

Both detect the server install the same way preparation does (`SE_SERVER_ROOT`
overrides detection) and print one line per discrepancy followed by a summary:

| Prefix | Meaning |
|--------|---------|
| `MISSING:` | recorded in `server_files.json`, absent from install |
| `MODIFIED:` | present but contents no longer hash to the recorded digest |
| `EXTRA:` | present in install but not recorded (added after the snapshot) |

Exit codes: `0` everything matches, `2` discrepancies found, `1` error (install or
hash file not found).

A failing verification usually means one of:

- server was updated but preparation has not been re-run — re-run it
- files were modified by a plugin loader (Magnetar, Torch), a mod, or a partial
  SteamCMD update
- install is corrupted — verify the files through SteamCMD

Extra arguments passed on to the underlying script, e.g. `-j 8` to limit the number
of hashing threads or `-q` to suppress progress output.

## Direct script use

```bash
# Write the digests (what preparation runs)
uv run hash_server_files.py --write "<ServerRoot>" Data

# Verify against them
uv run hash_server_files.py --verify "<ServerRoot>" Data
```

`<ServerRoot>` is the install root, **not** the `DedicatedServer64` subfolder;
passing `DedicatedServer64` is rejected because the recorded paths are relative to
the root. Hashing runs on a thread pool (`-j`, default: CPU count capped at 16).
