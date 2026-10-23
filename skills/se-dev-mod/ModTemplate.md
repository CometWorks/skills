# Mod Template

Template repository to build new Space Engineers mods: [se-mod-template](https://github.com/viktor-ferenczi/se-mod-template).
Works on Windows and Linux.

## Prerequisites

- [Space Engineers](https://store.steampowered.com/app/244850/Space_Engineers/)
- [Python 3.12](https://python.org) or newer, needed only for project setup
- [.NET 10 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)
- [.NET Framework 4.8.1 Developer Pack](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net481) (Windows only, recommended for Visual Studio)

Mod SDK not needed: project references game assemblies from game's own `Bin64` folder.

## Create your project

1. Click **Use this template** (top right corner on GitHub) and follow wizard to create your repository
2. Clone your repository for a local working copy
3. Run `setup.py`, enter name of your mod project in `CapitalizedWords` format
4. Let `setup.py` auto-detect game install location or fill it in manually
5. Open solution in Visual Studio or Rider, or build from command line with `dotnet build`
6. Build solution, it links `Mod` folder of project into game's local mods folder (build log shows path)
7. Add local mod to a world you use to test it during development
8. Replace contents of `README.md` with description of your mod intended for developers, link your workshop mod once published
9. Write code of your mod in `Mod/Data/Scripts` folder of project, follow TODO comments, see tutorials and source code of other mods as examples
10. Fill `SteamDescription.txt` file with description intended for players (use when you publish mod)
11. Create good thumbnail image in `Mod/thumb.jpg` (use when you publish mod)
12. After first publishing your mod, commit `modinfo.sbmi` file created by SE in `Mod` folder of project to your repository

_Good luck!_

## Remarks

### Project is for IDE only

Game compiles scripts under `Mod/Data/Scripts` itself when a world with mod loads.
DLL built by project never used by game: project exists for IDE support (code completion,
navigation, refactoring) and compile checks. References only assemblies game's mod compiler
references, so IDE does not offer APIs unavailable to mods.

Game compiles mods as C# 6, so project restricted to that language version.
Only whitelisted APIs usable from mods (see [ModApiWhitelist.txt](ModApiWhitelist.txt)): IDE cannot check that, game will tell.

### Folder path overrides

`Directory.Build.props` (committed) declares overridable folder paths with empty defaults:

- `Bin64` — folder containing `SpaceEngineers.exe`
- `Mods` — game's local mods folder, `Mod` folder linked into it after each build

Optionally imports `Directory.Build.props.user` from repository root, **not committed**
(matched by `*.user` in `.gitignore`), so each contributor keeps own local paths there.
`setup.py` writes that file with auto-detected install location, keeping any other overrides in it.
To override manually: copy first `PropertyGroup` of `Directory.Build.props` into
`Directory.Build.props.user`, wrapped into top-level `<Project>` element, fill in paths.

Empty path (or no `Directory.Build.props.user`) falls back to auto-detection: Steam registry keys
on Windows, usual Steam locations on Linux, then Steam's `libraryfolders.vdf` (finds secondary Steam libraries).

Local mods folder defaults:
- Windows: `%AppData%\SpaceEngineers\Mods`
- Linux: `~/.config/SpaceEngineers/Mods` if game runs natively via [Pulsar](https://github.com/SpaceGT/Pulsar),
  otherwise `Mods` folder inside game's Proton prefix (under `steamapps/compatdata/244850`).
  Native folder takes precedence if both exist.

Build fails with clear message if `Bin64` cannot be resolved, only warns if local mods folder cannot be resolved.

### Deployment

Each successful build links `Mod` folder of project into game's local mods folder as
`<Mods>/<ModName>`: directory junction on Windows, symlink on Linux. Game loads mod straight
from working copy, nothing to copy: rebuild or reload world after changing code.

Stale link (for example after moving working copy) recreated by next build. Real folder with
same name left untouched, build reports its path instead.

### Debugging your mod

1. Enable **Mod Debugging** plugin (`austinvaness/ModDebugBuild`) in Pulsar, it loads local mods in debuggable mode
2. Make sure build linked `Mod` folder into game's local mods folder (see build log)
3. Start game via Pulsar, then attach debugger of your IDE to game process
4. Load your test world, which has in-development mod loaded from its local folder
5. Set breakpoints in your mod's code

Remarks
- Hot reloading (changing code on the fly) may work, but generally unreliable.
- Debugging compatible with mod compilation cache of Performance Improvements plugin.
- On Linux game runs on .NET 10 via Pulsar, mod debugging there not verified yet.

## Troubleshooting

### Game does not pick up my source code changes

Once `Mod` folder linked into game's local mods folder, game loads scripts from working copy.
Load a world which has your local mod included. Will not work in multiplayer until you publish it on Steam.

If link missing or stale: rebuild project, look for deployment message in build log.
If real folder with mod's name exists in local mods folder (for example copy of mod),
delete it first, build never touches it.

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

### Debugger does not stop at my breakpoints

Path of source file in your IDE must match path of same file in game's local mods folder.

If they don't match (you copied source files instead of linking folder), IDE can't pair up
source files, therefore cannot establish breakpoints in assembly at runtime.

### Clean build

Run `clean.sh` (Linux) or `Clean.bat` (Windows) to delete `bin` and `obj` folders, then rebuild.
