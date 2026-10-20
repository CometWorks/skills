# Local runs vs. the players' PCs

When a player enables your plugin, Pulsar downloads your repository at the commit named in the hub
manifest and compiles it on their machine. That build differs from yours:

- **No MSBuild.** Your `.csproj`, `Directory.Build.props`, build events, resources, analyzers, source
  generators and implicit global usings are ignored. Pulsar compiles the `.cs` files under
  `SourceDirectories` with Roslyn as C# 14, in Release mode, with unsafe code allowed.
- **Committed files only.** Untracked files that a development folder picks up are missing on GitHub.
  Commit everything before you put the commit hash into the manifest.
- **Fixed references.** The game's DLLs plus Harmony, Newtonsoft.Json, Mono.Cecil, NLog, DiscordRPC and
  Microsoft.CSharp, and WinForms/WPF only on Windows. Anything else must come from `NuGetReferences` or an
  `Asset` in the manifest.
- **Different symbols.** Pulsar defines `PULSAR` and `TRACE`, `NETFRAMEWORK` on Legacy, `NETCOREAPP` on
  Interim and `LINUX` on Linux. `DEBUG` and the template's `LOCAL_BUILD` are not defined.
- **Random assembly name, no generated version.** Don't rely on `Assembly.GetName().Name` or the DLL's
  path. The template writes `[assembly: AssemblyVersion]` itself when `LOCAL_BUILD` is not defined.
- **Every flavor and platform.** Players run Legacy on Windows (.NET Framework), Legacy under Proton (Mono)
  and Interim on Windows and Linux (.NET 10). Test the ones you support and declare the rest out with
  `Runtimes` and `Platforms` in the manifest. Avoid Windows-only APIs if you support Linux.
- **No extra files.** Only compiled code arrives. Ship data files as assets and load them in `LoadAssets`.
  Store settings under `MyFileSystem.UserDataPath`, as the template's config does, never next to the game.
- **Other plugins.** Players combine your plugin with others that may patch the same methods. Test with
  popular plugins enabled.
- **Multiplayer.** A client plugin runs only on that player's PC. The server and the other players don't
  have it, so it can't change server-side behavior and must not break the server's authority.

Pulsar caches the compiled plugin and rebuilds it after a Pulsar or game update. Compile errors on a player's
machine end up in their `info.log`.
