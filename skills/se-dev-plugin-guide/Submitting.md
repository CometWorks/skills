# Submit to the hub

| Plugin | Hub | Folder |
|---|---|---|
| Client plugin | [StarCpt/PluginHub](https://github.com/StarCpt/PluginHub) | `Plugins/` |
| Client-side Workshop mod | [StarCpt/PluginHub](https://github.com/StarCpt/PluginHub) | `Plugins/Mods/` |
| Server plugin | [CometWorks/magnetar-hub](https://github.com/CometWorks/magnetar-hub) | `Plugins/` |
| Quasar UI plugin | [CometWorks/quasar-hub](https://github.com/CometWorks/quasar-hub) | `Plugins/` |

A plugin with a client and a server part goes to both PluginHub and MagnetarHub.

1. Make your repository public. You can develop in a private one, but the review needs public code.
2. Commit and push the release, and put its full hash into `Commit`.
3. Test exactly that commit: clone your fork of the hub, add your manifest, add the clone as a local hub in
   Pulsar's Sources dialog, disable the original hub and enable your plugin in Release mode.
4. Fork the hub, make a branch, add your manifest as `Plugins/<YourPlugin>.xml` and open a pull request,
   for example titled `Add Your Plugin`.
5. A check validates the XML. A maintainer then reviews your source code by hand, which takes time.

To release an update, open a pull request that changes only `Commit`, titled like `Your Plugin 1.2.0`.
Reviewers then read the changes between the two commits.

What reviewers look for, so your plugin gets through faster:

- Public source with a license; the commit is on the default branch.
- No committed DLLs or executables: use `NuGetReferences` or hashed `Asset` downloads.
- No telemetry, hidden network calls, self-updating code or obfuscation. Updates go through the hub.
- No changes to installed game or mod files; settings stay in the plugin's own data folder.
- No unfair advantage in multiplayer and no way around the server's authority.
- Patches that coexist with other plugins and don't cost noticeable performance.

A client-side Workshop mod (one that needs nothing on the server) can be listed too: search the
`Plugins/Mods` XML files for its Workshop ID first, then copy `SampleMod.xml` into `Plugins/Mods/`, fill it
in, test it through a local hub and open a pull request. The game keeps the mod up to date, so the file needs
no updates afterwards.

Give players a way to report bugs, and answer them. If you stop maintaining the plugin, look for a new
maintainer, say so in the README, ask for the hub entry to be hidden and keep the repository public so others
can fork it.
