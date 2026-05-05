# Mod Template

This is a template repository to build new Space Engineers mods.

## Prerequisites

- [Space Engineers](https://store.steampowered.com/app/244850/Space_Engineers/)
- Space Engineers - Mod SDK \*
- [Python 3.x](https://python.org) \**
- [.NET Framework 4.8.1 Developer Pack](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net481)

\* Install the Mod SDK via Steam. It is listed under Tools in your Library. You may need to enable listing the Tools in the drop-down at the top of the left side list.

\** Python is required only for the project setup. Tested with Python 3.11.

## Create your project

1. Click on **Use this template** (top right corner on GitHub) and follow the wizard to create your repository
2. Clone your repository to have a local working copy
3. Run `ReplaceGuidsAndRename.py`, enter the name of your mod project in `CapitalizedWords` format
4. Edit and run `Edit-and-run-before-opening-solution.bat` to link the `ModSDK` folder 
5. Open the solution in Microsoft Visual Studio or JetBrains Rider
6. Build the solution, it should deploy as a local mod into the `%APPDATA%\SpaceEngineers\Mods` folder
7. Add the local mod to a world you will use to test it during development
8. Delete `ReplaceGuidsAndRename.py` from the `Solution Items` folder of the solution (it is not needed anymore)
9. Replace the contents of this file with the description of your mod intended for developers, link your workshop mod once it is published
10. Write the code of your mod in the `ModTemplate` project, follow the TODO comments, see tutorials and the source code of other mods as examples
11. Fill the `SteamDescription.txt` file with the description intended for players (use this when you publish the mod)
12. Create a good thumbnail image in `Mod/Data/thumb.jpg` (use this when you publish the mod)
13. After you first publish your mod, make sure to commit the `modinfo.sbmi` file created by SE in the `Mod` subdirectory of the `ModTemplate` project to your repository  

_Good luck!_

## Debugging your mod

1. Install the **Mod Debugger** plugin in Plugin Loader
2. Make sure the `Deploy.bat` worked on building the project, it must create a symlink in `%AppData%\SpaceEngineers\Mods` to the `Mod` folder in your `ModTemplate` project
3. Run Plugin Loader's `SpaceEngineersLauncher.exe` in debug mode (a run config for Rider is provided)
4. Load your test world, which has the in-development mod loaded from its local folder
5. You should be able to set breakpoints in your mod's code now

Remarks
- Hot reloading (changing the code on the fly) may work, but is generally unreliable.
- Debugging is compatible with the mod compilation cache of the Performance Improvements plugin.

## Troubleshooting

### The game does not pick up my source code changes

You have to rebuild the project or invoke `Deploy.bat` manually to have your changes
deployed into the `%APPDATA%\SpaceEngineers\Mods\ModTemplate` folder.

Once deployed, you need to load a world which has your local mod included. It will
not work in multiplayer until you publish it on Steam.

### Accidentally deleted the `modinfo.sbmi` file

Recreate the file from this template, fill the missing IDs accordingly:

```xml
<?xml version="1.0"?>
<MyObjectBuilder_ModInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SteamIDOwner>YOUR-STEAM-ID</SteamIDOwner>
  <WorkshopId>0</WorkshopId>
  <WorkshopIds>
    <WorkshopId>
      <Id>WORKSHOP-ID-OF-YOUR-MOD</Id>
      <ServiceName>Steam</ServiceName>
    </WorkshopId>
  </WorkshopIds>
</MyObjectBuilder_ModInfo>
```

You can get the IDs from the Steam URLs. Your Steam profile link has your Steam ID in it. The link to your mod has an `id` URL parameter.

### The debugger does not stop at my breakpoints

The path of the source file in your IDE must be the same as the path of the same files in your local `%APPDATA%\SpaceEngineers\Mods\ModTemplate` folder.

If they do not match (your copied the source files instead of linking the folder), then the IDE won't be able to pair up the source files, therefore cannot establish the breakpoints in the assembly at runtime.