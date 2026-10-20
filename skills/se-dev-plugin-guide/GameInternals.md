# Learn the game's internals

Keen documents only the Mod and PB script APIs. Plugins can reach anything in the game, so you learn from
the game's code itself.

- **Decompiled game code.** The [`se-dev-game-code`](../se-dev-game-code/SKILL.md) skill decompiles the whole
  client with ILSpy and indexes it for search; [`se-dev-server-code`](../se-dev-server-code/SKILL.md) does the
  same for the dedicated server. Run `Prepare.bat` (Windows) or `prepare.sh` (Linux) in the skill's folder, or
  let the agent prepare it on first use. After a game update the skill decompiles again and can show what
  changed between the two versions, which helps keep a plugin working. Without the skill, open the DLLs in
  `Bin64` with [ILSpy](https://github.com/icsharpcode/ILSpy), dnSpyEx or Rider's decompiler.
- **Handbooks.** `se-dev-game-book` and `se-dev-server-book` explain how the client and the server work, by
  subsystem. They are distributed separately; if installed, read them before searching the code. The code wins
  where the two disagree.
- **Other plugins.** Every plugin on the hubs is open source. Find similar ones in the
  [plugin list](https://cometworks.github.io/plugins/se1/) and read how they do it. The
  [`se-dev-plugin`](../se-dev-plugin/SKILL.md) skill downloads and indexes them for search
  ([OtherPluginsAsExamples.md](../se-dev-plugin/OtherPluginsAsExamples.md)).
- **Mod and script API.** Many game types are also visible through the Mod API, and the Mod and PB script
  communities have years of examples (`se-dev-mod`, `se-dev-script`). Information from before 2019 is often
  outdated. Do not use Keen's old public source archive on GitHub: it is years behind the game.

**Never publish decompiled game or server code**, not in a repository, an issue or a pull request. It stays on
the developer's machine; it is Keen's property.
