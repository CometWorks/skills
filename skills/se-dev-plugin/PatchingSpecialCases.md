# Patching Special Cases

This document covers advanced Harmony features: finalizers, reverse patches, and auxiliary methods.

## Finalizers

Finalizers wrap the original method and all patches in a try/finally block. They are **guaranteed to execute** regardless of exceptions.

### When to Use Finalizers

- Suppress or remap exceptions
- Guarantee cleanup code runs
- Log all exceptions from a method

### Basic Finalizer

```csharp
[HarmonyPatch(typeof(MyClass), nameof(MyClass.RiskyMethod))]
static class ExceptionHandlerPatch
{
    // Observe exceptions without affecting them
    static void Finalizer(Exception __exception)
    {
        if (__exception != null)
            Log.Error($"RiskyMethod threw: {__exception.Message}");
    }
}
```

### Suppressing Exceptions

Return `null` to suppress:

```csharp
static Exception Finalizer(Exception __exception)
{
    if (__exception is ArgumentNullException)
    {
        Log.Warn("Suppressed ArgumentNullException");
        return null; // Exception suppressed
    }
    return __exception; // Rethrow others
}
```

### Remapping Exceptions

Return a different exception:

```csharp
static Exception Finalizer(Exception __exception)
{
    if (__exception != null)
        return new PluginException("Wrapped exception", __exception);
    return null;
}
```

### Finalizer with Result

Finalizers can also access `__result`:

```csharp
static Exception Finalizer(Exception __exception, ref int __result)
{
    if (__exception != null)
    {
        __result = -1; // Set fallback value
        return null;   // Suppress exception
    }
    return null;
}
```

## Reverse Patches

Reverse patches let you call the **original unpatched implementation** of a method, or copy a private method into your code.

### When to Use Reverse Patches

- Call the original method from within your patch
- Access private methods without reflection
- Get a "frozen" copy of a method's implementation

### Basic Reverse Patch

```csharp
[HarmonyPatch]
static class MyPatches
{
    // This stub will contain the original implementation
    [HarmonyReversePatch]
    [HarmonyPatch(typeof(MyClass), nameof(MyClass.Calculate))]
    static int OriginalCalculate(MyClass instance, int input)
    {
        // Stub - Harmony replaces this with the original code
        throw new NotImplementedException("Stub");
    }

    [HarmonyPatch(typeof(MyClass), nameof(MyClass.Calculate))]
    static class CalculatePatch
    {
        static bool Prefix(MyClass __instance, int input, ref int __result)
        {
            if (input < 0)
            {
                // Call the original for negative inputs
                __result = OriginalCalculate(__instance, input);
                return false;
            }
            return true; // Let modified version handle positive
        }
    }
}
```

### Reverse Patch Types

```csharp
// Get the original, unmodified IL
[HarmonyReversePatch(HarmonyReversePatchType.Original)]

// Get the method with existing transpilers applied
[HarmonyReversePatch(HarmonyReversePatchType.Snapshot)]
```

### Calling Private Methods

```csharp
[HarmonyReversePatch]
[HarmonyPatch(typeof(MyClass), "PrivateMethod")]
static void CallPrivateMethod(MyClass instance, string arg)
{
    throw new NotImplementedException("Stub");
}
```

**Warning:** For instance methods, ensure `this` types match. Static methods are safer.

## Auxiliary Methods

These methods control the patching lifecycle.

### Prepare

Called before patching. Return `false` to skip the patch:

```csharp
[HarmonyPatch(typeof(OptionalFeature), "DoThing")]
static class OptionalPatch
{
    static bool Prepare()
    {
        // Only apply if the target type exists
        return AccessTools.TypeByName("OptionalFeature") != null;
    }

    static void Postfix() { /* ... */ }
}
```

With parameters:

```csharp
static bool Prepare(MethodBase original, Harmony harmony)
{
    Log.Info($"Preparing to patch: {original?.Name ?? "null"}");
    return true;
}
```

**Note:** `Prepare` is called multiple times: once with `original = null`, then once per target method.

### Cleanup

Called after patching completes:

```csharp
static void Cleanup(MethodBase original, Exception ex)
{
    if (ex != null)
        Log.Error($"Failed to patch {original}: {ex.Message}");
}
```

Can intercept/replace exceptions:

```csharp
static Exception Cleanup(Exception ex)
{
    if (ex != null)
        Log.Error($"Patching failed: {ex}");
    return null; // Suppress the exception
}
```

### TargetMethod

Dynamically specify a single target method:

```csharp
[HarmonyPatch]
static class DynamicPatch
{
    static MethodBase TargetMethod()
    {
        var type = AccessTools.TypeByName("Some.Private.Type");
        return AccessTools.Method(type, "SomeMethod");
    }

    static void Prefix() { /* ... */ }
}
```

### TargetMethods

Apply the same patch to multiple methods:

```csharp
[HarmonyPatch]
static class MultiTargetPatch
{
    static IEnumerable<MethodBase> TargetMethods()
    {
        // Patch all "Update" methods in MyNamespace
        foreach (var type in AccessTools.AllTypes())
        {
            if (type.Namespace == "MyNamespace")
            {
                var method = AccessTools.Method(type, "Update");
                if (method != null)
                    yield return method;
            }
        }
    }

    static void Prefix(MethodBase __originalMethod)
    {
        Log.Info($"Update called on {__originalMethod.DeclaringType}");
    }
}
```

**Note:** `TargetMethods` must return at least one method. Use `Prepare` returning `false` if you need to skip entirely.

## Priority and Ordering

Control patch execution order:

```csharp
[HarmonyPatch(typeof(MyClass), "Method")]
[HarmonyPriority(Priority.High)] // Run before normal patches
static class HighPriorityPatch
{
    static void Prefix() { /* Runs first */ }
}

[HarmonyPatch(typeof(MyClass), "Method")]
[HarmonyPriority(Priority.Low)] // Run after normal patches
static class LowPriorityPatch
{
    static void Prefix() { /* Runs last */ }
}
```

Priority values (higher = runs first):
- `Priority.First` = 800
- `Priority.VeryHigh` = 600
- `Priority.High` = 500
- `Priority.Normal` = 400 (default)
- `Priority.Low` = 300
- `Priority.VeryLow` = 200
- `Priority.Last` = 0

For fine control:

```csharp
[HarmonyBefore("other.mod.id")]  // Run before specific mod
[HarmonyAfter("another.mod.id")] // Run after specific mod
```

## Patching Properties and Events

### Properties

```csharp
// Patch the getter
[HarmonyPatch(typeof(MyClass), nameof(MyClass.MyProperty), MethodType.Getter)]
static class PropertyGetterPatch
{
    static void Postfix(ref int __result)
    {
        __result = 42;
    }
}

// Patch the setter
[HarmonyPatch(typeof(MyClass), nameof(MyClass.MyProperty), MethodType.Setter)]
static class PropertySetterPatch
{
    static void Prefix(ref int value)
    {
        value = Math.Max(0, value);
    }
}
```

### Events

```csharp
// Patch the add accessor
[HarmonyPatch(typeof(MyClass), nameof(MyClass.MyEvent), MethodType.Adder)]
static class EventAddPatch { /* ... */ }

// Patch the remove accessor
[HarmonyPatch(typeof(MyClass), nameof(MyClass.MyEvent), MethodType.Remover)]
static class EventRemovePatch { /* ... */ }
```

## Patching Enumerator Methods

Methods returning `IEnumerable<T>` or `IEnumerator<T>` are compiled into state machines. The actual logic is in a compiler-generated `MoveNext` method:

```csharp
[HarmonyPatch]
static class EnumeratorPatch
{
    static MethodBase TargetMethod()
    {
        // Find the compiler-generated type
        var enumeratorType = AccessTools.Inner(typeof(MyClass), "<GetItems>d__5");
        return AccessTools.Method(enumeratorType, "MoveNext");
    }

    static void Postfix() { /* ... */ }
}
```

Alternatively, use a postfix with pass-through to filter results:

```csharp
[HarmonyPatch(typeof(MyClass), nameof(MyClass.GetItems))]
static class FilterPatch
{
    static IEnumerable<Item> Postfix(IEnumerable<Item> __result)
    {
        foreach (var item in __result)
        {
            if (item.IsValid)
                yield return item;
        }
    }
}
```

## See Also

- [Patching.md](Patching.md) - Basic patch structure
- [PatchInjections.md](PatchInjections.md) - Special parameters
- [TranspilerPatching.md](TranspilerPatching.md) - IL-level patching
- [AccessTools.md](AccessTools.md) - Finding methods dynamically
