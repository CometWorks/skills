General instructions:
- A server plugin project has two targets: the game **Client** (loaded by Pulsar) and the **Server** (loaded by Magnetar).
- Write the logic and patches into the `Shared` project. Add code in the target-specific projects (`ClientPlugin`, `ServerPlugin`) only if it belongs only to that target.
- Write all new patches using the Harmony patching library.

Targets:
- **Client** (`ClientPlugin`): runs inside the game client, loaded by [Pulsar](https://github.com/SpaceGT/Pulsar). Compiled with `!DEDICATED`.
- **Server** (`ServerPlugin`): runs inside the dedicated server, loaded by [Magnetar](https://magnetar.se). It builds against the Dedicated Server assemblies and is compiled with the `DEDICATED` conditional compilation symbol.

Building the project:
- In development the project is built by the `dotnet` command line tool or by an IDE like VSCode, JetBrains Rider or Visual Studio.
- The DLLs built are deployed to their respective "Local" plugin folders by each project's `Deploy.bat` (Windows) or `Deploy.sh` (Linux) script:
  - Client: into Pulsar's `Local` plugin folder
  - Server: into Magnetar's `Local` plugin folder (`%AppData%\Magnetar\Local` on Windows, `~/.config/Magnetar/Local` on Linux)
- In production server plugins are distributed as pre-built `Release` DLLs. They are registered into the [MagnetarHub](https://github.com/viktor-ferenczi/MagnetarHub) so Magnetar can list and load them. See [Guide.md](Guide.md) for the publishing workflow.

Runtime patching:
- Use Harmony for all patches. The client and server code can be patched the same way, most classes and methods are available on both. Some methods are running (used) only on the client, some only on the server, but most are used both on the server and the client.
- Each target (`ClientPlugin`, `ServerPlugin`) has a separate main `Plugin.cs` file with a `Plugin` class specific to that target. Start from there to understand the target.

Server-side configuration:
- The server plugin's configuration is declared and persisted through Magnetar's **PluginSdk**. Admins configure it remotely via [Quasar](https://github.com/viktor-ferenczi/Quasar) (the Magnetar control plane), which renders the UI layout the plugin declares.
- For declaring configuration variables, the remote UI layout, server-side chat commands, server lifecycle control and environment-agnostic logging, use the **`se-dev-plugin-sdk`** skill.
- The client side `Config` class (the in-game configuration dialog) is separate from the server side PluginSdk configuration.

Example patches:
- `Examples/Server/ExamplePatch.cs` Prefix and Postfix patches
- `Examples/Server/ExampleServerPatch.cs` Patch to run only on the server (gated by `#if DEDICATED`), not on the client
- `Examples/Server/ExampleTranspilerPatch.cs` Transpiler patch (see the IL files for its effect on the modified method's body)

Folder structure of a client-server (multi-targeted) plugin:
- `.idea`: JetBrains Rider settings (for convenience)
- `Docs`: Images linked from the README file or any further documentation should go here.
- `Shared`: Shared project with all the code which is used on at least one target, usually on both.
- `Shared/Config`: Shared configuration interface and persistence code.
- `Shared/Logging`: Shared logging interface and log formatting code.
- `Shared/Patches`: Use this folder and namespace to host the Harmony patches.
- `Shared/Plugin`: Shared plugin initialization and update handler code.
- `Shared/Tools`: Shared utility code for transpiler patches, detecting game code changes by IL code hash and checking if the game runs on Linux (Wine/Proton).
- `ClientPlugin`: The client target. Pulsar builds only the source code under this folder or its subdirectories. You can find plugin initialization, configuration and logging directly in this folder.
- `ClientPlugin/Settings`: Reusable configuration dialog components. See `Config.cs` in the project directory on usage examples.
- `ServerPlugin`: The server target, loaded by Magnetar. Code specific to the dedicated server goes here.

Conditional compilation for specific targets:
- `ServerPlugin` defines `DEDICATED`
- `ClientPlugin` is `!DEDICATED`

References:
- [Server plugin template](https://github.com/viktor-ferenczi/se-server-plugin-template) Template repository to start a new client + server plugin project.
- `se-dev-plugin-sdk` skill — Magnetar's PluginSdk handbook for server-side configuration, commands and lifecycle.
