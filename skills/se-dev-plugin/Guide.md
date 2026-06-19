# Plugin development guide

This guide was made for human plugin developers.

## Start with a template
Choose one of these templates, click the green "Use this template" button on GitHub to make your own repo, then clone that repo.

- Client only plugin template: https://github.com/CometWorks/client-plugin-template
- Client and server plugin template: https://github.com/CometWorks/server-plugin-template

**Follow the `README` after cloning your plugin project locally.**

*The server template is more complex. Has two targets — the game client (loaded by [Pulsar](https://github.com/SpaceGT/Pulsar)) and the dedicated server (loaded by [Magnetar](https://magnetar.se)) — plus a `Shared` project for code used by both. Need the server template only if your client plugin must have a server side companion plugin (like MGP) or is a server-only plugin. Server plugin's configuration is handled by Magnetar's PluginSdk (see the `se-dev-plugin-sdk` skill).*

*Good luck!*
### Channels
- Plugin ideas: #🙏🏼｜requests 
- Ask questions here: #📃｜chat
### Documentation
- Harmony patching library: https://harmony.pardeike.net/api/index.html
- Krafs publicizer: https://github.com/krafs/Publicizer

## Build, run and debug your plugin locally
Two ways to build and debug your client plugin locally:

- **Build from the IDE** and use the `Deploy.bat` which is run by the build process to **copy the DLL** into the `%AppData%\Pulsar\Legacy\Local` folder. Set up run configs to start `%AppData%\Pulsar\Legacy.exe` with debugging right from your IDE, which lets you debug your plugin code and most of the game's code. If you plan to debug, make a `Debug` build of your plugin. Recommended: pass the `-skipintro` option to Pulsar for faster startup and use the `Instant Exit` plugin for faster, cleaner shutdown.

- **Set up a "dev" folder in Pulsar's Sources dialog** for the plugin. Must pass the `-sources` option to Pulsar to access this dialog. This setup is essential for pre-release testing to make sure Pulsar can also build your plugin, because the IDE may build it but Pulsar fails with an error. Make Debug or Release builds inside a plugin dev folder. A Debug build should let your IDE connect the debugger to the `Legacy.exe` process (the game running in Pulsar). A Release build allows testing the exact same build players will have on their machines when they install your plugin. Once a dev folder is added in the Sources dialog, add that dev folder to the regular plugin list (and save in profiles). Assign the plugin's XML "info" file in the dialog you open by double clicking on your dev folder added to the Plugins list. *(BUG: Currently this association is not saved. There is a PR to fix this.)*

## Release your plugin

### Client plugins → PluginHub
- Fill in the fields of the `YourPluginName.xml` file in your project's folder.  (This file came with the plugin template. If you haven't used the template, find one in the [PluginHub](https://github.com/StarCpt/PluginHub/) repository.)
- Fork the [PluginHub](https://github.com/StarCpt/PluginHub/) repository and make a PR adding your XML file to the `Plugins` folder, where all plugins are defined.
- Wait for the PR to be merged. Involves a human reviewing your plugin's source code, so be patient.

Updating your plugin is the same workflow by changing your XML in the [PluginHub](https://github.com/StarCpt/PluginHub/). Pulsar lists and loads client plugins from the PluginHub.

### Server plugins → MagnetarHub
- Fill in the fields of the server plugin's XML descriptor that came with the server template.
- Fork the [MagnetarHub](https://github.com/CometWorks/magnetar-hub) repository and make a PR adding your XML file to the `Plugins` folder.
- Wait for the PR to be merged (a human reviews the source code).

Magnetar lists and loads server plugins from the MagnetarHub. Server admins configure them remotely through [Quasar](https://github.com/CometWorks/quasar), the Magnetar control plane, which lists the MagnetarHub plugins and renders each plugin's configuration UI.

## Pusar
### Paths 
- Main installation folder: `%AppData%\Pulsar`
- SE1 executable: `%AppData%\Pulsar\Legacy.exe`
- SE1 data files: `%AppData%\Pulsar\Legacy\`
- SE1 loader log file: `%AppData%\Pulsar\Legacy\info.log`
### Options

Copy: `-skipintro -nosplash -sources`
- `-skipintro`: Passed to the game to make it start faster
- `-nosplash`: Passed to the game to skip the splash window
- `-sources`: Enables access to the **Sources** dialog (developers only)
### Profiles
- Use **Profiles** to save separate `Development`, `Test` and `Production` plugin lists.
  - `Development`: Loads your plugins from DLL files.
  - `Test`: Loads your plugins from "dev" folders. Use before each release.
  - `Production`: Loads your plugins from the publicly visible source (PluginHub registered).

Add your usual plugins made by other developers to all the saved profiles above if you wish.

*Backup your profiles regularly. Also make a copy of each with a "Backup" suffix to protect you from mistakenly updating the wrong one.*
### Useful plugins for development
- `Instant Exit`: Makes the game stop faster and cleaner (kills itself), also prevents instances being stuck in the background.
- TODO: Add more

## FAQ
- *Which C# versions are supported?*
Plugins have no C# language version limit. The templates set `LangVersion` to `latestMinor`, so you get the latest language features your compiler supports. (Mods are limited to C# 7.3, PB scripts are limited to C# 6.0, because they are compiled by the game.)
- *Can I use NuGet packages?*
Yes. Must support `.net standard 2.0` or `.net framework 4.8`. (If you want your plugin usable with `Interim.exe` (.NET 10), then `.net standard 2.0` it is.)
- *Can I use additional data files?*
Bring them as asset files. Implement the `LoadAssets` method in your `Plugin` class.
- *Where can I find example source code to learn from?*
Look into the source code of other plugins (all open source on GitHub) to see how the basics work.
- *I have an older plugin and some software complains that its project file is not in "SDK format"*
Rebuild it based on the current template, so the project file is in "SDK format". Using VSCode requires the SDK format. Build your plugin from the command line using the `dotnet build` command. This also lets coding agents rebuild your project and fix errors/warnings automatically without your intervention if you use a "looping workflow" in your prompt.

## Registering a mod to Pulsar

Mods running only on client side (not requiring a server side mod being present) may be registered to Pulsar:

- First, check whether the mod is already present on Pulsar.
- Fork the [PluginHub](https://github.com/StarCpt/PluginHub/) and clone it using Git
- Double check whether the mod is already present by searching for the mod's workshop ID in the XML files under `Plugins/Mods`
- Make a new branch from `main`
- Copy `SampleMod.xml` from the repository root into `Plugins/Mods` and rename to match the mod's name
- Carefully fill in the fields of the XML file. Use the other XML files in that folder as examples
- Commit the new file into your branch and push it
- Open a PR from your branch to add the file to the PluginHub
- We will review the PR and merge it if the mod is acceptable

The mod will be updated by the game, so the XML file does not need changing anymore unless you need to fix some field in it.
