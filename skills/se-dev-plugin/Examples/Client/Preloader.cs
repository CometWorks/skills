// Uncomment the next line to enable preloader patching
//#define HAS_PRELOADER_PATCHES

#if HAS_PRELOADER_PATCHES

using System.Collections.Generic;
using Mono.Cecil;

// DO NOT USE A NAMESPACE HERE!
// CRITICAL: Using a namespace here will prevent Pulsar from finding the Preloader class.
// INTENTIONALLY COMMENTED OUT: namespace ClientPlugin;

public class Preloader
{
    // Full filenames of the game DLLs to patch (not full path)
    public static IEnumerable<string> TargetDLLs { get; } =
    [
        "Sandbox.Game.dll" // Example item
    ];

    // Runs before any of the preloader patches of any of the plugins
    public static void Initialize()
    {
        // TODO: Run any initialization required before patching
    }

    // Runs for each of the assemblies listed in TargetDLLs
    // CRITICAL: This is the AssemblyDefinition class from Mono.Cecil!
    public static void Patch(AssemblyDefinition assembly)
    {
        // TODO: Match the assembly name and patch the IL code in-place using Mono.Cecil
    }

    // Runs right before Space Engineers starts
    public static void Finish()
    {
        // TODO
    }
}

#endif