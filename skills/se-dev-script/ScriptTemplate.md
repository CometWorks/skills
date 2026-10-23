# Space Engineers In-game Script Template

Template repository for PB scripts: [se-script-template](https://github.com/viktor-ferenczi/se-script-template).
Comes with its own copy of the merge tool in `Merge` project (same options as [ScriptMerge.md](ScriptMerge.md)).

## Preparations

1. Use this template on GitHub to create your own script repository.
2. Clone your repository.
3. Open solution in your C# IDE (Rider or VS should work)
4. Build the `Merge` project (.NET Framework 4.8.1 console app, output `Merge\bin\Merge.exe`)

## Usage

### Write your code

- Add script's code to the `Script` project. 
- Use only C# 6 syntax in scripts.
- You can use multiple source code files or project as needed.
- From newly added script projects reference the `SpaceEngineers.ScriptingReferences` NuGet package.
- Keep all code which needs to go into final program in the `Script` namespace (merge tool default, change with `-n`).
- Add any unit tests into separate namespace or even project, for example `Tests`.
- Wrap all debug code into `#if DEBUG` directives.
- For debugging 3D math use the [(DevTool) Programmable Block DebugAPI](https://steamcommunity.com/sharedfiles/filedetails/?id=2654858862) mod and its PB API.

### Merge and deploy your script

Merge tool options (`Merge\bin\Merge.exe --help`, or `merge_help.bat`):

- `-n`, `--namespace` comma separated namespaces to merge [default: `Script`]
- `-d`, `--deploy` script name, writes `%AppData%\SpaceEngineers\IngameScripts\local\<name>\Script.cs`; prints merged script to stdout if not given
- `-m` minify, `-u` shorten names to single Unicode letters, `-a` aggressive compression (requires `-u`), `-r` release mode (removes `#if DEBUG` blocks)
- `-s`, `--solution` solution file [default: `*.sln` in current folder]

There is no `-o` option: the tool writes only into SE's local script folder, by script name.

- Test merging: `print_merged_script.bat` (`Merge\bin\Merge.exe -m`) or Rider run configurations `Print debug script` / `Print release script`
- Deploy: Rider run configurations `Deploy debug script` (`-m -d "Name Of My Script"`) and `Deploy release script` (`-m -a -u -r -d "Name Of My Script"`); change the script name in them
- The template's `deploy_*_script.bat` files still pass `-o "<path>\Script.cs"`, which the tool rejects: replace it with `-d "Name Of My Script"` before using them
- Deploying creates or overwrites `Script.cs` in the named script folder.

### Automatically updating code in PBs

Works only for offline and locally hosted multiplayer games.

- Enable the [ScriptDev](https://github.com/viktor-ferenczi/se-script-dev) plugin in Pulsar.
- Apply change and restart game.
- Load your world.
- Append script's name in square brackets to PB's name: `Programmable Block [Name Of My Script]`
- Plugin updates code in PB whenever `Script.cs` file changes (checks last modification time of file every second)

If script is in subdirectory, PB's name must include directories `/` separated. 

For example: `Programmable Block [My Subdir/Name Of My Script]`

### Shared code, multiple scripts

You can develop multiple scripts in same solution. You can also split code into any number of projects.
All that matters while merging script is the namespaces the tool takes code from. 

Put shared code into separate namespace, then use the `--namespace` (`-n`) option to select namespaces
to build script from. 

For example to develop two scripts in same solution use these namespaces:
- SharedCode
- FirstScript
- SecondScript

Then invoke merge tool with these parameters to deploy them separately:
- `-n SharedCode,FirstScript -d "First Script"`
- `-n SharedCode,SecondScript -d "Second Script"`

Template's own examples: Rider run configurations `Deploy release Inventory` (`-n InventoryScript -d Inventory`),
`Deploy release SorterCopier` and `Deploy release RSM`.

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
