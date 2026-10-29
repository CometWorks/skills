# Upgrading the skills to a new game version

Do this after each game update that changes the game's version label (for example `1.210.014`).
Work on a branch and open one PR with all of it.

1. **Update the game** through Steam and note the new label:
   `uv run skills/se-dev-game-code/check_version.py --print <Bin64>`.

2. **Re-prepare the code skills.** Run `prepare.sh` (Linux) or `Prepare.bat` (Windows) in
   `skills/se-dev-game-code` and `skills/se-dev-server-code`. They see the new version, decompile
   again and commit the result in their local `Data` repository, so you can diff the two versions
   there (`git -C Data diff HEAD~1 --stat`). Nothing from `Data` goes into this repository.

3. **Refresh the script and mod API whitelists** from the running game. The dump plugin in
   [tools/whitelist-dump](tools/whitelist-dump) reads them from `MyScriptCompiler.Static.Whitelist`
   once the game reaches the main menu, writes them out and exits the game. Pulsar Legacy and
   Interim both compile it from source as a DevFolder plugin. `dump.py` runs it in a Pulsar working
   folder of its own (it overwrites that folder's local plugins and profile):

   ```bash
   python3 tools/whitelist-dump/dump.py --pulsar <own Pulsar folder> --appdata <scratch folder> \
       --out <scratch folder>/whitelist [--bin64 <Bin64>]
   ```

   It prints `OK: game <version>, ...` and leaves in `--out`:

   | File | What to do with it |
   |---|---|
   | `PBApiWhitelist.txt` | copy to `skills/se-dev-script/` |
   | `ModApiWhitelist.txt` | copy to `skills/se-dev-mod/` |
   | `PBApiBlacklist.txt` | nothing; members the game takes away from PB scripts again, for reference |
   | `game-version.txt` | the version for step 4 |

   Ship the dump made on **Windows**, where `dump.py` runs Pulsar Legacy, the .NET Framework game
   that players run. On Linux it runs Pulsar Interim headless and offline, which needs no Steam and
   takes seconds, but the keys come out in .NET 10 form: `System.Private.CoreLib` instead of
   `mscorlib`, other `System.Linq` internals and newer `System` members. Use a Linux dump to see
   whether the game's rules changed: compare it with the shipped
   files after stripping the assembly names (`sed 's/, [^,]*$//'`).

   Then check that `uv run summarize_whitelist.py` still runs in both skill folders, and read the
   removed lines in `git diff`: a removed name that the skill docs use (`grep -rn <name> skills`)
   has to go from the docs too.

4. **Update the version mentions**: the whitelist lines in `skills/se-dev-script/SKILL.md` and
   `skills/se-dev-mod/SKILL.md`, and the FAQ answer "Does Claude Code know about the mod and script
   API whitelists?" in [README.md](README.md).

5. **Check the rest against the new version**: run the Graphify and index steps the prepare
   scripts report as stale, and search the skill docs for types or members the decompiled diff from
   step 2 shows as renamed or removed. The handbooks (`se-dev-game-book`, `se-dev-server-book`) live
   in their own repository and have their own refresh.
