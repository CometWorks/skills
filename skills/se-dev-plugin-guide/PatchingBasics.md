# Patching basics

Plugins change the game by patching its methods at runtime with [Harmony](https://harmony.pardeike.net/api/index.html).

- Prefer **prefix** and **postfix** patches. Declare them with `[HarmonyPatch]` attributes in the
  `Patches` folder; the template's `Plugin` applies them all with `PatchAll`. Look at the example patch
  there first.
- Use a **transpiler** only when a prefix or postfix can't do it. It rewrites the method's IL once, at
  load, so it can't depend on runtime state, and it breaks more easily when the game or another plugin
  changes the same method. The templates can record the IL before and after your patch.
- **Preloader patches** (Mono.Cecil, the template's `Preloader.cs`) are a last resort: for inlined
  methods, changed signatures or code that runs in static constructors. They slow down game loading.
- To reach private and internal members without reflection, enable the
  [Krafs Publicizer](https://github.com/krafs/Publicizer) as the template's README describes, and list the
  assemblies in `GameAssembliesToPublicize.cs`. Pulsar publicizes the same assemblies when it compiles your
  plugin. Without it use Harmony's `AccessTools`.
- Use a unique Harmony ID and never call `UnpatchAll()`: it removes other plugins' patches too.
- Pulsar ships Harmony 2.4.2; don't bundle your own.
- The server template's `[EnsureCode("hash")]` attribute checks that a patched method's code hasn't changed
  since you wrote the patch, so a game update disables the patch instead of crashing the game.

Details, step by step, in the `se-dev-plugin` skill: [Patching.md](../se-dev-plugin/Patching.md) (prefix and
postfix), [PatchInjections.md](../se-dev-plugin/PatchInjections.md) (`__instance`, `__result`, fields),
[AccessTools.md](../se-dev-plugin/AccessTools.md), [TranspilerPatching.md](../se-dev-plugin/TranspilerPatching.md),
[PatchingSpecialCases.md](../se-dev-plugin/PatchingSpecialCases.md), [PreloaderPatching.md](../se-dev-plugin/PreloaderPatching.md)
and [Publicizer.md](../se-dev-plugin/Publicizer.md).
