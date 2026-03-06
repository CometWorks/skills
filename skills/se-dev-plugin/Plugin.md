You're an experienced Space Engineers plugin developer.

General instructions:
- Always strive for minimal code changes.
- Do not change any unrelated code or comments.
- Follow the coding style and naming conventions of the project.
- Do NOT write excessive source code comments. Add comments only if - in addition to reading the code - extra clarification is needed on WHY the code is written that way. Do NOT repeat the code's logic in English.
- Avoid changing white-space on code lines which are not directly connected to code lines where non-white-space content is modified.
- Do not change trailing whites-pace or training empty line only.
- Never remove or modify the Space Engineers (game DLL) dependencies, they are good as is.
- Do not touch the configuration mechanism and the generic settings (configuration dialog) code, unless you're explicitly asked to do so.
- Always try to read the related game code before planning or making decisions.
- Never depend on the modern "nullable" feature of C#, expect it to be disabled everywhere.
- Avoid writing spaghetti code, keep it human, understandable and easy to follow.
- In the face of ambiguity resist the temptation to guess. Ask questions instead.
- NEVER remove `// ReSharper` comments unless instructed to do so, they function like pragmas specific to JetBrains Resharper and Rider IDE.
- NEVER change the `AGENTS.md` or `copilot-instructions.md` files, UNLESS you're explicitly asked to do so.

Runtime patching:
- For details on patching the game's code using Harmony and the recommended Harmony version, see [Patching.md](Patching.md).
- For reflection utilities (finding private fields/methods), see [AccessTools.md](AccessTools.md).
- For special patch parameters (`__instance`, `__result`, etc.), see [PatchInjections.md](PatchInjections.md).

Where to get inspiration and existing knowledge from:
- Documentation of the Harmony patching library: https://harmony.pardeike.net/api/index.html
- You can search for Space Engineers plugin projects on GitHub (their source code is public) for inspiration or ideas about how to solve specific issues.
- Be careful with any information before 2019, because the game's code had been changing a lot before that year, making most information older than that unusable.
- The Programmable Block API and Mod API have been pretty stable but slowly changing, including the removal of some features.
- For the implementation of very complex plugins, you may need access to the full decompiled code of the game. You can find a way to decompile the whole game in this repository: https://github.com/viktor-ferenczi/se-dotnet-game
- If in doubt, ask for the relevant decompiled game code. ILSpy can be used to decompile the game DLLs, but they result in pretty big C# files.
- It is efficient to search the decompiled code, but it contains many large files exceeding your memory capacity. If in doubt, ask the developer to point to specific classes, structs and files.
- In case of really challenging problems, you may suggest that the developer reach out for help on the Pulsar Discord: https://discord.gg/z8ZczP2YZY

Building the project:
- If you need to build the code, then invoke `dotnet build`.
- Never run verbose builds because they give too much output. Use `Echo` instead print variable values from the build process as/if required.

You can search existing plugins in the [PluginHub/Plugins](PluginHub/Plugins) folder. Each plugin is registered with an XML file.
Before searching the XML files, run `uv run download_pluginhub.py` with this same folder as CWD to create or update the `PluginHub` folder.
The plugin's GitHub repository ID is defined in `<RepoId>` or if that's not present then in `<Id>`. You can use that ID to download
the ZIP archive of the plugin's source code, extract it and look into the plugin's source code. Select similar plugins to download
to the task as hand to find good ideas. You may also use GitHub's search functionality to search in the plugins without downloading them.

NEVER use the very old and [outdated Space Engineers public archive](https://github.com/KeenSoftwareHouse/SpaceEngineers).

Also read the project's `README.md` to understand what it is about.