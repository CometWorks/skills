General instructions:
- A server plugin project has two targets: the game **Client** (loaded by Pulsar) and the **Server** (loaded by Magnetar).
- Write logic and patches into `Shared` project. Add code in target-specific projects (`ClientPlugin`, `ServerPlugin`) only if it belongs only to that target.
- Write all new patches using Harmony patching library.

Targets:
- **Client** (`ClientPlugin`): runs inside game client, loaded by [Pulsar](https://github.com/SpaceGT/Pulsar). Compiled with `!DEDICATED`.
- **Server** (`ServerPlugin`): runs inside dedicated server, loaded by [Magnetar](https://magnetar.se). Builds against Dedicated Server assemblies and compiled with `DEDICATED` conditional compilation symbol.

Building the project:
- In development project is built by `dotnet` command line tool or by IDE like VSCode, JetBrains Rider or Visual Studio.
- DLLs built are deployed to their respective "Local" plugin folders by each project's `Deploy.bat` (Windows) or `Deploy.sh` (Linux) script:
  - Client: into Pulsar's `Local` plugin folder
  - Server: into Magnetar's `Local` plugin folder (`%AppData%\Magnetar\Local` on Windows, `~/.config/Magnetar/Local` on Linux)
- In production server plugins distributed as pre-built `Release` DLLs. Registered into [MagnetarHub](https://github.com/CometWorks/magnetar-hub) so Magnetar can list and load them. See [Guide.md](Guide.md) for publishing workflow.

Runtime patching:
- Use Harmony for all patches. Client and server code can be patched same way, most classes and methods available on both. Some methods run (used) only on client, some only on server, but most used on both server and client.
- Each target (`ClientPlugin`, `ServerPlugin`) has separate main `Plugin.cs` file with `Plugin` class specific to that target. Start from there to understand target.

Server-side configuration:
- Server plugin's configuration declared and persisted through Magnetar's **PluginSdk**. Admins configure it remotely via [Quasar](https://github.com/CometWorks/quasar) (Magnetar control plane), which renders UI layout the plugin declares.
- For declaring configuration variables, remote UI layout, server-side chat commands, server lifecycle control and environment-agnostic logging, use **`se-dev-plugin-sdk`** skill.
- Client side `Config` class (in-game configuration dialog) is separate from server side PluginSdk configuration.

Example patches:
- `Examples/Server/ExamplePatch.cs` Prefix and Postfix patches
- `Examples/Server/ExampleServerPatch.cs` Patch to run only on server (gated by `#if DEDICATED`), not on client
- `Examples/Server/ExampleTranspilerPatch.cs` Transpiler patch (see IL files for its effect on modified method's body)

Folder structure of a client-server (multi-targeted) plugin:
- `.idea`: JetBrains Rider settings (for convenience)
- `Docs`: Images linked from README file or any further documentation go here.
- `Shared`: Shared project with all code used on at least one target, usually on both.
- `Shared/Config`: Shared configuration interface and persistence code.
- `Shared/Logging`: Shared logging interface and log formatting code.
- `Shared/Patches`: Use this folder and namespace to host Harmony patches.
- `Shared/Plugin`: Shared plugin initialization and update handler code.
- `Shared/Tools`: Shared utility code for transpiler patches, detecting game code changes by IL code hash and checking if game runs on Linux (Wine/Proton).
- `ClientPlugin`: Client target. Pulsar builds only source code under this folder or its subdirectories. Find plugin initialization, configuration and logging directly in this folder.
- `ClientPlugin/Settings`: Reusable configuration dialog components. See `Config.cs` in project directory for usage examples.
- `ServerPlugin`: Server target, loaded by Magnetar. Code specific to dedicated server goes here.

Conditional compilation for specific targets:
- `ServerPlugin` defines `DEDICATED`
- `ClientPlugin` is `!DEDICATED`

References:
- [Server plugin template](https://github.com/CometWorks/server-plugin-template) Template repository to start a new client + server plugin project.
- `se-dev-plugin-sdk` skill — Magnetar's PluginSdk handbook for server-side configuration, commands and lifecycle.
