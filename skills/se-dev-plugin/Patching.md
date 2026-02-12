# Harmony Patching

## Overview

- The patching library used is Harmony (HarmonyLib)
- The HarmonyLib version should match Pulsar's version (currently 2.4.2)
- Harmony allows changing IL code at runtime after game assemblies are loaded
- Patches are applied when loading the game

Before writing a plugin with patches, consider whether the implementation is possible as a Programmable Block script (PB API) or a mod (Mod API). Usually it is not, if writing a plugin comes up as a solution.

## Patch Types

| Type | When It Runs | Primary Use |
|------|--------------|-------------|
| **Prefix** | Before the original | Modify arguments, skip original, set up state |
| **Postfix** | After the original | Modify return value, read final state |
| **Transpiler** | Once at patch time | Rewrite IL instructions |
| **Finalizer** | After everything (in try/finally) | Handle exceptions, guaranteed cleanup |

For most tasks, **prefix and postfix patches** are sufficient. Use transpilers only when you must modify logic in the middle of a method.

## Basic Patch Structure

```csharp
using HarmonyLib;

[HarmonyPatch(typeof(TargetClass), nameof(TargetClass.TargetMethod))]
static class MyPatch
{
    static void Prefix()
    {
        // Runs before TargetMethod
    }

    static void Postfix()
    {
        // Runs after TargetMethod
    }
}
```

Harmony automatically discovers patch classes decorated with `[HarmonyPatch]` when you call `harmony.PatchAll()`.

## Prefix Patches

Prefixes run before the original method. They can:
- Read or modify arguments
- Skip the original method entirely
- Set up state for the postfix

### Reading Arguments

Match parameter names exactly:

```csharp
[HarmonyPatch(typeof(MyClass), nameof(MyClass.DoSomething))]
static class DoSomethingPatch
{
    // Original: void DoSomething(string name, int count)
    static void Prefix(string name, int count)
    {
        Log.Info($"DoSomething called with name={name}, count={count}");
    }
}
```

### Modifying Arguments

Use `ref` to modify arguments before the original runs:

```csharp
static void Prefix(ref int count)
{
    count = Math.Max(count, 1); // Ensure count is at least 1
}
```

### Skipping the Original Method

Return `false` to skip the original (and remaining prefixes):

```csharp
static bool Prefix()
{
    if (ShouldSkip())
        return false; // Skip original method
    return true; // Continue normally
}
```

When skipping, you often need to set `__result`:

```csharp
static bool Prefix(ref bool __result)
{
    if (CachedResult != null)
    {
        __result = CachedResult.Value;
        return false; // Skip original, use our result
    }
    return true;
}
```

**Best Practice:** Avoid skipping the original unless necessary. Postfixes and transpilers are preferred for compatibility with other patches.

## Postfix Patches

Postfixes run after the original method. They can:
- Read or modify the return value
- Access final argument values
- Read state set by a prefix

### Reading the Result

```csharp
static void Postfix(bool __result)
{
    Log.Info($"Method returned: {__result}");
}
```

### Modifying the Result

Use `ref` to change the return value:

```csharp
static void Postfix(ref int __result)
{
    __result *= 2; // Double the return value
}
```

### Pass-Through Pattern

For `IEnumerable` results or when you need to wrap the result:

```csharp
static IEnumerable<int> Postfix(IEnumerable<int> __result)
{
    foreach (var item in __result)
    {
        if (item > 0)
            yield return item; // Filter out non-positive values
    }
}
```

### Accessing Arguments

Postfixes can read arguments (but not usefully modify them):

```csharp
static void Postfix(string name, int __result)
{
    Log.Info($"Processing {name} returned {__result}");
}
```

## Passing State Between Prefix and Postfix

Use `__state` to pass data from prefix to postfix. Both must be in the same class:

```csharp
[HarmonyPatch(typeof(MyClass), nameof(MyClass.ExpensiveOperation))]
static class TimingPatch
{
    static void Prefix(out Stopwatch __state)
    {
        __state = Stopwatch.StartNew();
    }

    static void Postfix(Stopwatch __state)
    {
        __state.Stop();
        Log.Info($"Operation took {__state.ElapsedMilliseconds}ms");
    }
}
```

## Patching Instance Methods

For instance methods, use `__instance` to access the object:

```csharp
static void Prefix(MyClass __instance)
{
    Log.Info($"Called on instance: {__instance.Name}");
}
```

## Patching Constructors

```csharp
[HarmonyPatch(typeof(MyClass), MethodType.Constructor)]
[HarmonyPatch(new[] { typeof(int), typeof(string) })] // Parameter types
static class ConstructorPatch
{
    static void Postfix(MyClass __instance)
    {
        // Initialize additional state after construction
    }
}
```

## Conditional Patching with Prepare

Use `Prepare` to conditionally apply patches:

```csharp
[HarmonyPatch(typeof(OptionalClass), "OptionalMethod")]
static class ConditionalPatch
{
    static bool Prepare()
    {
        // Only patch if the feature is enabled
        return Settings.FeatureEnabled;
    }

    static void Postfix() { /* ... */ }
}
```

## Important Rules

1. **All patch methods must be static** - Harmony stores method pointers
2. **Never extend `Init` with manual `harmony.Patch` calls** - Use attributes instead
3. **Match parameter names exactly** - Or use `[HarmonyArgument]` attribute
4. **Use `ref` for output/modification** - Reading doesn't require `ref`

## Further Reading

- [PatchInjections.md](PatchInjections.md) - All special parameters (`__instance`, `__result`, `___fields`, etc.)
- [AccessTools.md](AccessTools.md) - Reflection utilities for finding methods and fields
- [TranspilerPatching.md](TranspilerPatching.md) - IL-level patching for complex cases
- [PatchingSpecialCases.md](PatchingSpecialCases.md) - Finalizers, reverse patches, auxiliary methods
- [PreloaderPatching.md](PreloaderPatching.md) - Pre-JIT patching

## References

- Full Harmony documentation: https://harmony.pardeike.net/articles/intro.html
