# Space Engineers In-game Script Template

## Preparations

1. Use this template on GitHub to create your own script repository.
2. Clone your repository.
3. Open solution in your C# IDE (Rider or VS should work)
4. Build the `Merge` project

## Usage

### Write your code

- Add script's code to the `Script` project. 
- Use only C# 6 syntax in scripts.
- You can use multiple source code files or project as needed.
- From newly added script projects reference the `SpaceEngineers.ScriptingReferences` NuGet package.
- Keep all code which needs to go into final program in the `Script` namespace.
- Add any unit tests into separate namespace or even project, for example `Tests`.
- Wrap all debug code into `#if DEBUG` directives.
- For debugging 3D math use the [(DevTool) Programmable Block DebugAPI](https://steamcommunity.com/sharedfiles/filedetails/?id=2654858862) mod and its PB API.

### Merge and deploy your script

- Test merging of script by running `print_*_script.bat` or your IDE's run configuration (Rider: `Print * script`)
- Customize output path in `deploy_*_script.bat` and in your IDE's run configurations (Rider: `Deploy * script`)
- Run a deploy script command. Creates or overwrites the output `Script.cs` file you specified.

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

Put shared code into separate namespace, then use the `--namespaces` (`-n`) option to select namespaces
to build script from. 

For example to develop two scripts in same solution use these namespaces:
- SharedCode
- FirstScript
- SecondScript

Then invoke merge tool with these parameters to deploy them separately:
- `-n SharedCode,FirstScript -o "%AppData%\SpaceEngineers\IngameScripts\local\FirstScript\Script.cs"`
- `-n SharedCode,SecondScript -o "%AppData%\SpaceEngineers\IngameScripts\local\SecondScript\Script.cs"`

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