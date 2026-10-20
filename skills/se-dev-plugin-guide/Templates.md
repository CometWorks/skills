# Pick a template

| Template | Pick it when | Loaded by | Hub |
|---|---|---|---|
| [client-plugin-template](https://github.com/CometWorks/client-plugin-template) | The plugin runs only in the game client. This is most plugins. | Pulsar | [PluginHub](https://github.com/StarCpt/PluginHub) |
| [server-plugin-template](https://github.com/CometWorks/server-plugin-template) | The plugin needs a server-side companion (like Multigrid Projector) or runs only on the dedicated server. | Pulsar + Magnetar | PluginHub + [MagnetarHub](https://github.com/CometWorks/magnetar-hub) |
| [quasar-plugin-template](https://github.com/CometWorks/quasar-plugin-template) | You extend the [Quasar](https://github.com/CometWorks/quasar) server control panel's web UI. | Quasar | [QuasarHub](https://github.com/CometWorks/quasar-hub) |

The server template has three projects: `ClientPlugin`, `ServerPlugin` and `Shared`, a shared project
compiled into both. Delete the project you don't need; for a single project, move the code out of
`Shared` and delete it. For a Torch plugin use the template's `last-torch-compatible` tag, not `main`:
Torch plugins don't run on Magnetar and Magnetar plugins don't run on Torch.

Prerequisites: Space Engineers, [Pulsar](https://github.com/SpaceGT/Pulsar), the .NET 10 SDK, Python 3.12
or newer, and on Windows the .NET Framework 4.8.1 Developer Pack. The server template also needs the
Space Engineers Dedicated Server and [Magnetar](https://github.com/CometWorks/magnetar).

Start a project:

1. On GitHub click **Use this template** and create your repository, then clone it.
2. Run `setup.py` and give the plugin's name in `CapitalizedWords` form. It renames the projects and files,
   generates new GUIDs (one is the manifest's `Id`) and writes the detected game folder into
   `Directory.Build.props.user`, which is not committed.
3. Open the solution in Visual Studio, Rider or VS Code and build it once.
4. Load it into the game as a development folder (see [Test your plugin locally](LocalTesting.md)) and check
   that the empty plugin can be enabled.
5. Replace the README with your plugin's description and follow the `TODO` comments in the code.

Read the template's README; it covers the configuration dialog, debugging, transpiler and preloader
patches and the publicizer. The plugin's version is in `Version.Build.props`.

On Windows the projects build for `net48` (the `Legacy` Pulsar flavor) and `net10.0` (the `Interim`
flavor). On Linux they build only for `net10.0`.

Have an old plugin whose project is not in "SDK format"? Start over from the current template and move the
logic across. A coding agent does that port well.
