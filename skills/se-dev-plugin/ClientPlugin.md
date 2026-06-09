Building the project:
- In production the plugin is built by the Pulsar plugin loader directly on the player's machine.
- In development the plugin is built either of these ways:
  - By the `dotnet` command line tool or by an IDE like VSCode, JetBrains Rider or Visual Studio. Then the DLL built is deployed to Pulsar's `Local` plugin folder by the `Deploy.bat` (Windows) or `Deploy.sh` (Linux) script.
  - By Pulsar using the local development folder feature (needs to be configured in Pulsar). This requires the plugin's XML definition file to have the right content.
- Any additional NuGet dependencies added by the plugin must also be listed in the `<NuGetReferences>` element of the plugin's XML descriptor (see the `<PackageReference>` example in `ClientPluginTemplate.xml`), so Pulsar pulls them for plugin compilation.
- See `ClientPluginTemplate.xml` (or `PluginHub/SamplePlugin.xml`) for the example syntax of the plugin's XML definition.

Targeting both .NET Framework and .NET 10:
- On Windows the project builds for both `net48` (the `Legacy` runtime) and `net10.0` (the `Interim` runtime). On Linux it builds only for `net10.0`.
- Use the `<Runtimes>` tag in the plugin XML descriptor to restrict which runtimes the plugin loads on, if needed.

Example patches:
- `Examples/Client/ExamplePrefixPostfixPatch.cs` Prefix and Postfix patches
- `Examples/Client/ExampleTranspilerPatch.cs` Transpiler patch (see the IL files for its effect on the modified method's body)

Folder structure of a client-only plugin:
- `.run`: JetBrains Rider run configurations (for convenience)
- `Docs`: Images linked from the README file or any further documentation should go here.
- `ClientPlugin`: Pulsar builds only the source code under this folder or its subdirectories. You can find plugin initialization, configuration and logging directly in this folder.
- `ClientPlugin/Settings`: Reusable configuration dialog components. See `Config.cs` in the project directory on usage examples.
- `ClientPlugin/Tools`: Utility code for transpiler and preloader patches, game code change detection by IL hash, and access-check helpers.
- `ClientPlugin/Patches`: Use this folder and namespace to host the Harmony patches.
- `ClientPlugin/Preloader.cs`: Preloader (pre-JIT) patching entry point. See [PreloaderPatching.md](PreloaderPatching.md).

References:
- [Client plugin template](https://github.com/viktor-ferenczi/se-client-plugin-template) Template repository to start a new project.
