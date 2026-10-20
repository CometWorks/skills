# Test your plugin locally

## Pulsar's files

Pulsar installs into `%AppData%\Pulsar` on Windows and `~/.config/Pulsar` on Linux. Each flavor has a data
folder there:

| Flavor | Runs | Executable | Data folder |
|---|---|---|---|
| Legacy | SE1 on .NET Framework 4.8 (Windows only) | `Legacy.exe` | `Legacy\` |
| Interim | SE1 on .NET 10 (Windows and Linux) | `Interim.exe`, `Interim.bin` on Linux | `Interim\` if that folder exists, otherwise `Legacy\` |
| Modern | SE2 | `Modern.exe`, `Modern.bin` | `Modern\` |

Pulsar's log is `info.log` in the data folder; on Windows the game's own log is in `%AppData%\SpaceEngineers`. Create an
empty `Interim` folder next to `Legacy` to give the .NET 10 flavor its own profiles and plugin cache, so you
can test both flavors without one overwriting the other. A Pulsar update wipes the install folder except the
data folders, so keep nothing else there.

Useful command-line options:

- `-sources` shows the **Sources** button, which developers need.
- `-noSplash` skips the splash window. Pulsar skips the intro video by default (`-keepIntro` brings it
  back), so the `-skipintro` in older guides is no longer needed.
- `-profile <name>` starts with a given profile; `-safeMode` starts with all user plugins disabled.
- `-debug` launches the debugger at startup; `-debugCompileAll` compiles every plugin and lists the ones that
  fail to compile or initialize.

## Way 1: a development folder (recommended)

Pulsar compiles your working copy from source, just as it compiles hub plugins on the players' PCs.

1. Start Pulsar with `-sources` and click **Sources**.
2. Under Plugins click **Add Development Folder** and pick your repository's folder.
3. When asked, select the plugin's manifest XML (the one in the repository root). Pulsar takes the name,
   `SourceDirectories`, NuGet packages, assets and dependencies from it.
4. Enable the new entry in the plugin list. Choose Debug or Release in its settings.

A **Debug** build has symbols with embedded source: attach your IDE's debugger to `Legacy.exe` or
`Interim.exe` and set breakpoints in your plugin and in most of the game. A **Release** build is exactly
what players get. New dev folders default to Debug, so switch to Release before your final test.

Pulsar compiles only the `.cs` files: the tracked and untracked but not ignored files under
`SourceDirectories`. It never runs MSBuild, so a project that builds in the IDE can still fail here. That
is why this test matters.

## Way 2: deploy the DLL from the IDE

Builds deploy nothing by default. Set `Pulsar` in `Directory.Build.props.user` (`$(APPDATA)\Pulsar` on
Windows, `$(HOME)/.config/Pulsar` on Linux) or pass `-p:Pulsar=...` to `dotnet build`. Each build then
copies `plugin.dll`, `plugin.pdb` and the manifest as `plugin.xml` into `Legacy\Local\<PluginName>` (the
`net48` build) and `Interim\Local\<PluginName>` (the `net10.0` build). Set up a run configuration in your
IDE that starts `Legacy.exe` or `Interim.exe` with the debugger attached.

This is the fastest loop for debugging, but the deployed DLL shows up as a separate local plugin. Remove it
when you are done: if it stays enabled it hides the published version. Stop the game before building, or the
old DLL is locked.

## Profiles

Save separate plugin lists as profiles and switch between them:

- **Development**: your plugin from the DLL deployed by the IDE.
- **Test**: your plugin from the development folder. Run it before each release, in Release mode.
- **Production**: your plugin from the hub, as players have it.

Add the other plugins you use to all three. Back up the profiles, and keep a copy of each with a `Backup`
suffix in case you save over the wrong one.

## Server plugins

Magnetar uses the same mechanisms: a `Local` folder and development folders. Register a development folder
with `MagnetarConfig` (F8, **Local & Dev Folders**, pick the manifest XML), or under Quasar's dev folders if
you run the server from Quasar. The server template can deploy the `net10.0` build into `<MagnetarData>/Local`
when `MagnetarData` is set. Server plugins declare their configuration, chat commands and Quasar UI through
Magnetar's PluginSdk; see the
[`se-dev-plugin-sdk`](https://github.com/CometWorks/magnetar/tree/main/skills/se-dev-plugin-sdk) handbook.

## Linux

Develop natively: Pulsar's Linux build (`Interim.bin`) runs Space Engineers without Wine or Proton, and
debugging works the same way as on Windows. The templates build only for `net10.0` there.
