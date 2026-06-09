# Mod Template

Template repository to build new Space Engineers mods.

## Prerequisites

- [Space Engineers](https://store.steampowered.com/app/244850/Space_Engineers/)
- Space Engineers - Mod SDK \*
- [Python 3.x](https://python.org) \**
- [.NET Framework 4.8.1 Developer Pack](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net481)

\* Install Mod SDK via Steam. Listed under Tools in your Library. May need to enable listing Tools in drop-down at top of left side list.

\** Python required only for project setup. Tested with Python 3.11.

## Create your project

1. Click **Use this template** (top right corner on GitHub) and follow wizard to create your repository
2. Clone your repository for a local working copy
3. Run `ReplaceGuidsAndRename.py`, enter name of your mod project in `CapitalizedWords` format
4. Edit and run `Edit-and-run-before-opening-solution.bat` to link `ModSDK` folder 
5. Open solution in Microsoft Visual Studio or JetBrains Rider
6. Build solution, should deploy as local mod into `%APPDATA%\SpaceEngineers\Mods` folder
7. Add local mod to a world you use to test it during development
8. Delete `ReplaceGuidsAndRename.py` from `Solution Items` folder of solution (not needed anymore)
9. Replace contents of this file with description of your mod intended for developers, link your workshop mod once published
10. Write code of your mod in `ModTemplate` project, follow TODO comments, see tutorials and source code of other mods as examples
11. Fill `SteamDescription.txt` file with description intended for players (use when you publish mod)
12. Create good thumbnail image in `Mod/Data/thumb.jpg` (use when you publish mod)
13. After first publishing your mod, commit `modinfo.sbmi` file created by SE in `Mod` subdirectory of `ModTemplate` project to your repository  

_Good luck!_

## Debugging your mod

1. Install **Mod Debugger** plugin in Plugin Loader
2. Ensure `Deploy.bat` worked on building project, it must create symlink in `%AppData%\SpaceEngineers\Mods` to `Mod` folder in your `ModTemplate` project
3. Run Plugin Loader's `SpaceEngineersLauncher.exe` in debug mode (run config for Rider provided)
4. Load your test world, which has in-development mod loaded from its local folder
5. You can set breakpoints in your mod's code now

Remarks
- Hot reloading (changing code on the fly) may work, but is generally unreliable.
- Debugging is compatible with mod compilation cache of Performance Improvements plugin.

## Troubleshooting

### The game does not pick up my source code changes

Rebuild project or invoke `Deploy.bat` manually to deploy your changes
into `%APPDATA%\SpaceEngineers\Mods\ModTemplate` folder.

Once deployed, load a world which has your local mod included. Will
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

Get IDs from Steam URLs. Your Steam profile link has your Steam ID in it. Link to your mod has an `id` URL parameter.

### The debugger does not stop at my breakpoints

Path of source file in your IDE must match path of same files in your local `%APPDATA%\SpaceEngineers\Mods\ModTemplate` folder.

If they don't match (you copied source files instead of linking folder), IDE can't pair up source files, therefore cannot establish breakpoints in assembly at runtime.