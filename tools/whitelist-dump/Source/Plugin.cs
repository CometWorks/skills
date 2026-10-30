using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using Sandbox;
using VRage.Game;
using VRage.FileSystem;
using VRage.Plugins;
using VRage.Scripting;
using VRage.Utils;

namespace WhitelistDump;

// Writes the script whitelists of the running game into WHITELIST_DUMP_DIR, then exits the game:
//   PBApiWhitelist.txt   keys with the Ingame target, minus the ingame blacklist
//   ModApiWhitelist.txt  keys with the ModApi target
//   game-version.txt     the game version they came from
// Keys are in the game's own form ("Namespace.*, Assembly", "Type+*, Assembly", "Type.Member, Assembly"),
// in registration order. Keys of plugin assemblies (Pulsar's core plugins whitelist some of their own
// types) are left out. Does nothing without WHITELIST_DUMP_DIR.
public class Plugin : IPlugin
{
    private static readonly string Dir = Environment.GetEnvironmentVariable("WHITELIST_DUMP_DIR");

    private bool done;

    public void Init(object gameInstance)
    {
        MyLog.Default.WriteLine($"WhitelistDump: loaded, target {Dir ?? "(none)"}");
    }

    // The game fills the whitelist while it starts, so wait for the first frame that has it
    public void Update()
    {
        if (done || string.IsNullOrEmpty(Dir))
            return;
        var whitelist = MyScriptCompiler.Static?.Whitelist;
        if (whitelist == null || whitelist.GetWhitelist().Count == 0)
            return;
        done = true;

        var keys = whitelist.GetWhitelist().Where(p => FromGame(p.Key)).ToList();
        var blacklist = whitelist.GetBlacklistedIngameEntries();
        var ingame = keys.Where(p => p.Value.HasFlag(MyWhitelistTarget.Ingame) && !blacklist.Contains(p.Key))
            .Select(p => p.Key)
            .ToList();
        var modApi = keys.Where(p => p.Value.HasFlag(MyWhitelistTarget.ModApi)).Select(p => p.Key).ToList();
        var version = MyFinalBuildConstants.APP_VERSION_STRING_DOTS.ToString();

        Directory.CreateDirectory(Dir);
        File.WriteAllLines(Path.Combine(Dir, "PBApiWhitelist.txt"), ingame);
        File.WriteAllLines(Path.Combine(Dir, "ModApiWhitelist.txt"), modApi);
        File.WriteAllLines(Path.Combine(Dir, "PBApiBlacklist.txt"), blacklist);
        File.WriteAllText(Path.Combine(Dir, "game-version.txt"), version + "\n");
        MyLog.Default.WriteLine(
            $"WhitelistDump: DONE {version}, {ingame.Count} ingame and {modApi.Count} mod API keys, "
                + $"{blacklist.Count} blacklisted, written to {Dir}"
        );
        MySandboxGame.ExitThreadSafe();
    }

    // True for keys of the game's and the runtime's assemblies, false for plugin assemblies.
    // By file name: Pulsar loads the game's assemblies from its own preloaded copies.
    private static bool FromGame(string key)
    {
        var name = key.Substring(key.LastIndexOf(", ", StringComparison.Ordinal) + 2) + ".dll";
        return File.Exists(Path.Combine(MyFileSystem.ExePath, name))
            || File.Exists(Path.Combine(RuntimeEnvironment.GetRuntimeDirectory(), name));
    }

    public void Dispose() { }
}
