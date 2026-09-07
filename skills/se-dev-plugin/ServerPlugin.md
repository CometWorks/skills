General instructions:
- A server plugin project has two targets: the game **Client** (loaded by Pulsar) and the **Server** (loaded by Magnetar).
- Write logic and patches into `Shared` project. Add code in target-specific projects (`ClientPlugin`, `ServerPlugin`) only if it belongs only to that target.
- `Shared` is an MSBuild *shared project* (`Shared.shproj` / `Shared.projitems`), imported by both target projects, not a separate assembly.
- Write all new patches using Harmony patching library.

Targets:
- **Client** (`ClientPlugin`): runs inside game client, loaded by [Pulsar](https://github.com/SpaceGT/Pulsar). Compiled with the `PULSAR` conditional compilation symbol.
- **Server** (`ServerPlugin`): runs inside dedicated server, loaded by [Magnetar](https://magnetar.se). Builds against Dedicated Server assemblies and compiled with the `MAGNETAR` conditional compilation symbol.

Building the project:
- In development project is built by `dotnet` command line tool or by IDE like VSCode, JetBrains Rider or Visual Studio.
- On Windows both targets build for `net48` and `net10.0`; on Linux only for `net10.0`. `LangVersion` is `14`.
- Deployment is automatic: each project has a `DeployPlugin` MSBuild target that runs after a successful build. There are no `Deploy.bat` / `Deploy.sh` scripts.
  - Client: into Pulsar's `Local` plugin folder — `<Pulsar>/Legacy/Local/<PluginName>/` for the `net48` build, `<Pulsar>/Interim/Local/<PluginName>/` for the `net10.0` build (falling back to `Legacy` when `Interim` does not exist). Copied as `plugin.dll`, `plugin.pdb` and `plugin.xml`.
  - Server: into Magnetar's `Local` folder inside Magnetar's **config** folder — `<Magnetar>\MagnetarLegacy\Local` or `<Magnetar>\MagnetarInterim\Local` on Windows (named after the launcher), `$XDG_CONFIG_HOME/Magnetar/Local` (`~/.config/Magnetar/Local`) on Linux. Magnetar scans `Local` recursively and identifies a plugin by its DLL file name, so the files are deployed flat: `<AssemblyName>.dll`, `<AssemblyName>.pdb` and the MagnetarHub registration XML as `<AssemblyName>.dll.xml`.
- Folder paths are declared empty in `Directory.Build.props` and auto-detected, overridable in the uncommitted `Directory.Build.props.user` at the repository root (written by `setup.py`):
  - `Bin64`: folder containing `SpaceEngineers.exe`
  - `Dedicated64`: folder containing `SpaceEngineersDedicated.exe`
  - `Pulsar`: Pulsar folder the client plugin is deployed into
  - `Magnetar`: Magnetar installation folder holding the launchers and their `Libraries`, which is where `PluginSdk.dll` is referenced from
  - `MagnetarData`: Magnetar config folder the server plugin is deployed into (the one holding `Local`, `Sources`, `Profiles`)
  - The build fails with a clear message if `Bin64`, `Dedicated64` or `PluginSdk.dll` cannot be resolved, and only warns if a loader folder is missing.
- The plugin version lives in `Version.Build.props` (committed, imported by `Directory.Build.props`).
- In production server plugins distributed as pre-built `Release` DLLs. Registered into [MagnetarHub](https://github.com/CometWorks/magnetar-hub) so Magnetar can list and load them. See [Guide.md](Guide.md) for publishing workflow.

Runtime patching:
- Use Harmony for all patches. Client and server code can be patched same way, most classes and methods available on both. Some methods run (used) only on client, some only on server, but most used on both server and client.
- Each target (`ClientPlugin`, `ServerPlugin`) has separate main `Plugin.cs` file with `Plugin` class specific to that target, both implementing `VRage.Plugins.IPlugin` and the shared `ICommonPlugin`. Start from there to understand target.

Server-side configuration:
- As shipped, the template's `ServerPlugin` persists its configuration with `PersistentConfig<PluginConfig>` from `Shared/Config`, into a `<PluginName>.cfg` file under `MyFileSystem.UserDataPath`. The same shared config classes back the client's in-game configuration dialog.
- The `ServerPlugin` project references Magnetar's **PluginSdk** (`PluginSdk.dll`, resolved from `$(MagnetarBinDir)`, required for the build; not copied, the Magnetar host provides it at runtime). The shipped skeleton only references it, it does not call into it yet.
- Use PluginSdk for declaring configuration variables, remote UI layout, server-side chat commands, server lifecycle control and environment-agnostic logging. Admins then configure the plugin remotely via [Quasar](https://github.com/CometWorks/quasar) (Magnetar control plane), which renders the UI layout the plugin declares. See the **`se-dev-plugin-sdk`** skill (in the Magnetar repository) for that API.
- Client side `Config` class (in-game configuration dialog) is separate from server side PluginSdk configuration.

Example patches (copies kept in this skill, mirroring the template):
- `Examples/Server/ExamplePatch.cs` Prefix and Postfix patches (`Shared/Patches/` in the template)
- `Examples/Server/ExampleServerPatch.cs` Patch to run only on server (`ServerPlugin/Patches/` in the template, so no conditional compilation is needed)
- `Examples/Server/ExampleTranspilerPatch.cs` Transpiler patch (`Shared/Patches/` in the template; see IL files for its effect on modified method's body)

Folder structure of a client-server (multi-targeted) plugin:
- `.idea`: JetBrains Rider project settings (for convenience)
- `.vscode`, `.github`, `.clinerules`, `AGENTS.md`: instruction files for coding agents
- `Docs`: Images linked from README file or any further documentation go here.
- `Shared`: Shared project with all code used on at least one target, usually on both.
- `Shared/Config`: Shared configuration interface and persistence code.
- `Shared/Logging`: Shared logging interface and log formatting code.
- `Shared/Patches`: Use this folder and namespace to host Harmony patches used by both targets.
- `Shared/Plugin`: Shared plugin initialization and update handler code (`Common.cs`, `ICommonPlugin.cs`).
- `Shared/Tools`: Shared utility code for transpiler and preloader patches, detecting game code changes by IL code hash (`CodeChange.cs`, `EnsureCode.cs`, `Hashing.cs`), publicizer support and access-check helpers.
- `ClientPlugin`: Client target. Pulsar builds only source code under the directories listed in `<SourceDirectories>` of the client XML descriptor (`ClientPlugin` and `Shared`). Holds `Plugin.cs` and `Config.cs`; logging and tools live in `Shared`.
- `ClientPlugin/Settings`: Reusable configuration dialog components. See `Config.cs` in project directory for usage examples.
- `ServerPlugin`: Server target, loaded by Magnetar. Code specific to dedicated server goes here (`Plugin.cs`).
- `ServerPlugin/Patches`: Harmony patches that apply only to the dedicated server.
- Repository root: `setup.py` (one-time project setup and rename), `PluginTemplateClient.xml` and `PluginTemplateServer.xml` (PluginHub and MagnetarHub registrations, renamed by `setup.py`), `Directory.Build.props`, `Version.Build.props`, `Clean.bat` / `clean.sh`, the `.sln` file.

Conditional compilation for specific targets:
- `ClientPlugin` defines `PULSAR`
- `ServerPlugin` defines `MAGNETAR`
- Both define `LOCAL_BUILD` when built locally (IDE or `dotnet`), used to gate the assembly version attributes that the loader supplies when it compiles the sources itself. `DEBUG` is defined in Debug builds.
- There is no `DEDICATED` symbol. Code that belongs to a single target goes into that target's own project instead of being gated.

References:
- [Server plugin template](https://github.com/CometWorks/server-plugin-template) Template repository to start a new client + server plugin project.
- `se-dev-plugin-sdk` skill — Magnetar's PluginSdk handbook for server-side configuration, commands and lifecycle.
