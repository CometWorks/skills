# In-game Script Merge Tool for Space Engineers

`ScriptMerge` is command line tool for merging in-game scripts from multiple source code files. 

Can also minify script for release, so it fits under 100k characters limit. 

Please consider supporting my work on [Patreon](https://www.patreon.com/semods) or one time via [PayPal](https://www.paypal.com/paypalme/vferenczi/).

## Create a script project

- Install .NET Framework 4.8.1 (if you don't have it)
- Create .Net Framework 4.8.1 Class Library project
- Configure project for C# 6.0 syntax
- Reference these NuGet packages from project:
  - `SpaceEngineers.ScriptingReferences`
  - `System.Collections.Immutable` 
- Use the `Script/Skeleton.cs` file from this repository as starting point for your script code
- See `TODO` comments in skeleton for more
- See **Hints** below

## Merge your script

Build and use `IngameScriptMergeTool` to merge script source into single file:

### Help 

`IngameScriptMergeTool --help`

```
Description:
  Command line tool to merge a Space Engineers script from multiple source code files.

Usage:
  IngameScriptMergeTool [options]

Options:
  -s, --solution <solution>    Path to the solution file, it must include all projects your script depends on [default: *.sln]
  -n, --namespace <namespace>  Comma separated list of namespaces containing the code to be merged into the script [default: Script]
  -d, --deploy <deploy>        Deploy the script into SE's IngameScripts folder with this name (prints to stdout if not given)
  -m, --minify                 Minify the source code by removing all comments and most unnecessary whitespace [default: False]
  -u, --unicode                Shorten all names to single Unicode letters, exclusion: //! KeepThisName [default: False]
  -a, --aggressive             Aggressively compress code (reduces repeated string literals) (requires --unicode) [default: False]
  -r, --release                Enables release mode, it removes #ifdef DEBUG ... #endif blocks [default: False]
  --version                    Show version information
  -?, -h, --help               Show help and usage information
```

### Examples

- Print debug merge: `IngameScriptMergeTool`
- Print release merge: `IngameScriptMergeTool -maur` 
- Deploy debug merge: `IngameScriptMergeTool -d "Name Of My Script"`
- Deploy release merge: `IngameScriptMergeTool -maur -d "Name Of My Script"` 

Deployment target is SE's script folder: `%AppData%\SpaceEngineers\IngameScript\local\Name Of My Script`

## Hints

- For debugging 3D math use the [(DevTool) Programmable Block DebugAPI](https://steamcommunity.com/sharedfiles/filedetails/?id=2654858862) mod and its PB API
- Add unit tests (if any) into separate namespace (for example `Tests`)
- Wrap all debug code into `#if DEBUG` directives
- Subdirectories allowed, use `/` as delimiter, for example: `My Subdir/Name Of My Script`

### Excluding names from shortening

- Specific names (everywhere): `//! KeepThisName, KeepThatName`
- On the line of declaration: `const string DontRenameThis = "x"; //!`
- Enum values, sometimes they are shown to the player: `KeepThisEnumValue, //!`

### Header

Adding `//!!` anywhere in namespace declaration moves that namespace block to
top of merged script and excludes it from variable renaming and minification.
Useful to add documentation and configuration supposed to be editable by player. 

```cs
namespace Script {
    //!!
    /* Example script */
    static class Config {
        // Configuration variable
        public static ConfigVar = 1; 
    }
}
```

### Automatically updating code in PBs

- Enable the [ScriptDev](https://github.com/viktor-ferenczi/se-script-dev) plugin in Pulsar, Apply, restart SE.
- Append script's name in square brackets to PB's name: `Programmable Block [Name Of My Script]`
- Plugin updates code in PB whenever `Script.cs` file changes.

### Debug and release only code

Wrap debug and release code into directives as in regular C# code:

```cs
#if DEBUG
    Echo("DEBUG");
#endif

#if !DEBUG
    Echo("RELEASE");
#endif
```

Directives themselves are removed, only their body preserved during merging.

### Multiple scripts with code sharing

You can develop multiple scripts in same solution. You can also split code into any number of projects.
All that matters while merging script is the namespaces the tool takes code from. 

Put shared code into separate namespace, then use the `--namespaces` (`-n`) option to select namespaces
to build script from. 

For example to develop two scripts in same solution use these namespaces:
- SharedCode
- FirstScript
- SecondScript

Then invoke merge tool with these parameters to deploy them separately:
- `-n SharedCode,FirstScript -d "First Script"`
- `-n SharedCode,SecondScript -d "Second Script"`

### PB API whitelist checking

Simpler tool than MDK, does not depend on Visual Studio. However, currently does not verify
script against PB API whitelist. Could be implemented based on same whitelist
file of MDK, should enough script developers request it. Type information already available,
since required for proper minification.
