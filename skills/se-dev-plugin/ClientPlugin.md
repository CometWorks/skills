Building the project:
- In production the plugin is built by the Pulsar plugin loader directly on player's machine.
- In development the plugin is built either of these ways:
  - By the `dotnet` command line tool or by an IDE like VSCode, JetBrains Rider or Visual Studio. Deployment is automatic: the `DeployPlugin` MSBuild target in `ClientPlugin/ClientPlugin.csproj` runs after every successful build and copies the output into Pulsar's `Local` plugin folder. There are no `Deploy.bat` / `Deploy.sh` scripts.
    - `net48` build goes to `<Pulsar>/Legacy/Local/<PluginName>/`
    - `net10.0` build goes to `<Pulsar>/Interim/Local/<PluginName>/`, falling back to `Legacy` when `<Pulsar>/Interim` does not exist. (`<Pulsar>/Modern` belongs to SE2 and is never a target.)
    - Files are copied as `plugin.dll`, `plugin.pdb` and the registration XML from the repository root as `plugin.xml`, so Pulsar picks up the friendly name and the runtime/platform restrictions.
  - By Pulsar using local development folder feature (needs configuring in Pulsar's Sources dialog, which requires the `-sources` option). Requires plugin's XML definition file to have right content.
- Folder paths are declared empty in `Directory.Build.props` and auto-detected (Steam registry keys on Windows, usual Steam locations plus `libraryfolders.vdf` on Linux):
  - `Bin64`: folder containing `SpaceEngineers.exe`
  - `Pulsar`: Pulsar folder the plugin is deployed into (`%AppData%\Pulsar` on Windows, `$XDG_CONFIG_HOME/Pulsar` or `~/.config/Pulsar` on Linux)
  - Override them in `Directory.Build.props.user` at the repository root, which is **not** committed. `setup.py` writes that file with the auto-detected locations when the project is first set up.
- The plugin version lives in `Version.Build.props` (committed, imported by `Directory.Build.props`).
- Any additional NuGet dependencies added by the plugin must also be listed in the `<NuGetReferences>` element of plugin's XML descriptor (see the `<PackageReference>` example in `ClientPluginTemplate.xml`), so Pulsar pulls them for plugin compilation.
- See `ClientPluginTemplate.xml` (or `PluginHub/SamplePlugin.xml`) for example syntax of plugin's XML definition.

Targeting both .NET Framework and .NET 10:
- On Windows the project builds for both `net48` (the `Legacy` runtime) and `net10.0` (the `Interim` runtime). On Linux it builds only for `net10.0`.
- `LangVersion` is set to `14` in the project file.
- Use the `<Runtimes>` tag in plugin XML descriptor to restrict which runtimes the plugin loads on, if needed (`NETFramework`, `NETCoreApp`, case sensitive, comma separated).

Example patches (copies kept in this skill, mirroring `ClientPlugin/Patches/` in the template):
- `Examples/Client/ExamplePrefixPostfixPatch.cs` Prefix and Postfix patches
- `Examples/Client/ExampleTranspilerPatch.cs` Transpiler patch (see IL files for its effect on modified method's body)

Folder structure of a client-only plugin:
- `.idea`: JetBrains Rider project settings (for convenience)
- `.vscode`, `.github`, `.clinerules`, `AGENTS.md`: instruction files for coding agents
- `Docs`: Images linked from README file or further documentation go here.
- `ClientPlugin`: Pulsar builds only source code under the directories listed in `<SourceDirectories>` of the XML descriptor, which is this folder. Find plugin initialization and configuration directly in this folder (`Plugin.cs`, `Config.cs`).
- `ClientPlugin/Settings`: Reusable configuration dialog components. See `Config.cs` in project directory for usage examples.
- `ClientPlugin/Tools`: Utility code for transpiler and preloader patches, IL hashing, publicizer support and access-check helpers.
- `ClientPlugin/Patches`: Use this folder and namespace to host Harmony patches. Ships with the two example patches and their IL dumps.
- `ClientPlugin/Preloader.cs`: Preloader (pre-JIT) patching entry point, disabled by default. Enable it by uncommenting `#define HAS_PRELOADER_PATCHES` at the top of the file. See [PreloaderPatching.md](PreloaderPatching.md).
- Repository root: `setup.py` (one-time project setup and rename), `ClientPluginTemplate.xml` (PluginHub registration, renamed by `setup.py`), `Directory.Build.props`, `Version.Build.props`, `Clean.bat` / `clean.sh`, the `.sln` file.

References:
- [Client plugin template](https://github.com/CometWorks/client-plugin-template) Template repository to start new project.
