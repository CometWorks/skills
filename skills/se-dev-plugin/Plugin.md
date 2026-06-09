You're experienced Space Engineers plugin developer.

General instructions:
- Always strive for minimal code changes.
- Do not change any unrelated code or comments.
- Follow coding style and naming conventions of project.
- Do NOT write excessive source code comments. Add comments only if - beyond reading code - extra clarification needed on WHY code written that way. Do NOT repeat code's logic in English.
- Avoid changing white-space on code lines not directly connected to code lines where non-white-space content modified.
- Do not change trailing whites-pace or training empty line only.
- Never remove or modify Space Engineers (game DLL) dependencies, they are good as is.
- Do not touch configuration mechanism and generic settings (configuration dialog) code, unless explicitly asked to do so.
- Always try to read related game code before planning or making decisions.
- Never depend on modern "nullable" feature of C#, expect it disabled everywhere.
- Avoid spaghetti code, keep it human, understandable and easy to follow.
- In face of ambiguity resist temptation to guess. Ask questions instead.
- NEVER remove `// ReSharper` comments unless instructed to do so, they function like pragmas specific to JetBrains Resharper and Rider IDE.
- NEVER change the `AGENTS.md` or `copilot-instructions.md` files, UNLESS explicitly asked to do so.

Runtime patching:
- For details on patching game's code using Harmony and recommended Harmony version, see [Patching.md](Patching.md).
- For reflection utilities (find private fields/methods), see [AccessTools.md](AccessTools.md).
- For special patch parameters (`__instance`, `__result`, etc.), see [PatchInjections.md](PatchInjections.md).

Where to get inspiration and existing knowledge from:
- Documentation of Harmony patching library: https://harmony.pardeike.net/api/index.html
- Search Space Engineers plugin projects on GitHub (source code public) for inspiration or ideas how to solve specific issues.
- Be careful with any information before 2019, because game's code changed a lot before that year, making most information older than that unusable.
- Programmable Block API and Mod API have been stable but slowly changing, including removal of some features.
- For very complex plugins, you may need full decompiled code of game. Find way to decompile whole game in this repository: https://github.com/viktor-ferenczi/se-dotnet-game
- If in doubt, ask for relevant decompiled game code. ILSpy can decompile game DLLs, but they result in big C# files.
- Efficient to search decompiled code, but it has many large files exceeding your memory capacity. If in doubt, ask developer to point to specific classes, structs and files.
- For really challenging problems, you may suggest developer reach out for help on Pulsar Discord: https://discord.gg/z8ZczP2YZY

Building the project:
- To build code, invoke `dotnet build`.
- Never run verbose builds, they give too much output. Use `Echo` instead to print variable values from build process as/if required.

Search existing plugins in [PluginHub/Plugins](PluginHub/Plugins) folder. Each plugin registered with XML file.
Before searching XML files, run `uv run download_pluginhub.py` with this same folder as CWD to create or update `PluginHub` folder.
Plugin's GitHub repository ID defined in `<RepoId>` or if not present then in `<Id>`. Use that ID to download
ZIP archive of plugin's source code, extract it and look into plugin's source code. Select similar plugins to download
for task at hand to find good ideas. You may also use GitHub's search to search in plugins without downloading them.

NEVER use the very old and [outdated Space Engineers public archive](https://github.com/KeenSoftwareHouse/SpaceEngineers).

Also read project's `README.md` to understand what it is about.