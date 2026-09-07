/* TODO: If you need transpiler patches, then uncomment and understand this example patch. Otherwise it is safe to delete together with the *.il files next to it.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using Sandbox.Engine.Physics;
using Shared.Config;
using Shared.Tools;

namespace Shared.Patches;

// ReSharper disable once UnusedType.Global
[HarmonyPatch(typeof(MyPhysics))]
public static class MyPhysicsPatch
{
    private static IPluginConfig Config => Plugin.Common.Config;
    
    // ReSharper disable once UnusedMember.Local
    [HarmonyTranspiler]
    [HarmonyPatch(nameof(MyPhysics.LoadData))]
    private static IEnumerable<CodeInstruction> LoadDataTranspiler(IEnumerable<CodeInstruction> instructions, MethodBase patchedMethod, ILGenerator ilGenerator)
    {
        // Make your patch configurable.
        // Here it needs restarting the game, since patching happens only once.
        // Alternatively patch unconditionally, but make the functionality configurable
        // inside your logic, so changing the config does not need restarting the game.
        // There is a trade-off with performance and plugin compatibility here.
        if (!Config.Enabled) // Config.MyFeature
            return instructions;
        
        // This call will create a .il file next to this patch file with the original
        // IL code of the patched method. Compare that with the modified IL code (see below).
        // It is good practice to commit these IL files into your project for later reference,
        // so you can instantly see any changes in the game's code after game updates.
        var il = instructions.ToList();
        il.RecordOriginalCode(patchedMethod);
        
        // You may want to verify whether the game's code has changed on an update.
        // If this check fails, then your plugin will fail to load with a clean error
        // message. It allows you to look into game code changes efficiently and fix
        // your patch in the next version of your plugin. This check will also fail
        // if another plugin loaded before yours has already patched the same method.
        il.VerifyCodeHash(patchedMethod, "2bb5480c");

        // Modify the IL code of the method as needed to remove/replace game code.
        // Make sure to keep the stack balanced and don't delete labels which are still in use.
        // Use ilGenerator.DefineLabel() to define new labels (sometimes required).
        // Use ilGenerator.DeclareLocal() to create new local variables (usually not required).
        // You can remove the ilGenerator argument if it remains unused. 
        // Some example logic follows:
        var havokThreadCount = Math.Min(16, Environment.ProcessorCount);
        var i = il.FindIndex(ci => ci.opcode == OpCodes.Stloc_0);
        il.Insert(++i, new CodeInstruction(OpCodes.Ldc_I4, havokThreadCount));
        il.Insert(++i, new CodeInstruction(OpCodes.Stloc_0));

        // This call will create a .il file next to this patch file with the modified
        // IL code of the patched method. Compare this with the original (see above).
        // It is good practice to commit these IL files into your project for later reference,
        // so you can instantly see any changes in the game's code after game updates.
        il.RecordPatchedCode(patchedMethod);
        return il;
    }
}

*/