# Patch Injections

Harmony automatically injects special values into patch methods based on parameter names and types. This page documents all available injections.

## Quick Reference

| Parameter | Type | Purpose |
|-----------|------|---------|
| `__instance` | Same as patched class | The `this` reference (instance methods only) |
| `__result` | Same as return type | The method's return value |
| `__state` | Any type | Pass data from prefix to postfix |
| `___fieldName` | Same as field type | Access private fields (3 underscores) |
| `__args` | `object[]` | All arguments as an array |
| `__originalMethod` | `MethodBase` | The patched method's reflection info |
| `__runOriginal` | `bool` | Whether original will/did run |
| Named parameters | Match original | Access method arguments |

## Instance Access: `__instance`

For instance methods, `__instance` gives you the object the method was called on:

```csharp
[HarmonyPatch(typeof(MyEntity), nameof(MyEntity.Update))]
static class UpdatePatch
{
    static void Prefix(MyEntity __instance)
    {
        // Access instance members
        Log.Info($"Updating entity: {__instance.EntityId}");
    }
}
```

**Note:** Not available for static methods.

## Return Value: `__result`

Access or modify the method's return value:

```csharp
// Reading (postfix only - prefix sees default value)
static void Postfix(int __result)
{
    Log.Info($"Method returned: {__result}");
}

// Modifying
static void Postfix(ref int __result)
{
    __result = __result * 2;
}

// Setting when skipping original (prefix)
static bool Prefix(ref bool __result)
{
    __result = true;
    return false; // Skip original
}
```

The type must match or be assignable from the original return type.

## State Passing: `__state`

Pass data from prefix to postfix. Both patches must be in the same class:

```csharp
[HarmonyPatch(typeof(MyClass), nameof(MyClass.Process))]
static class ProcessPatch
{
    // Use 'out' in prefix to initialize
    static void Prefix(out long __state)
    {
        __state = DateTime.Now.Ticks;
    }

    // State is automatically passed to postfix
    static void Postfix(long __state)
    {
        var elapsed = DateTime.Now.Ticks - __state;
        Log.Info($"Elapsed ticks: {elapsed}");
    }
}
```

For complex state, use a custom type:

```csharp
struct PatchState
{
    public Stopwatch Timer;
    public string OriginalValue;
}

static void Prefix(out PatchState __state, string input)
{
    __state = new PatchState
    {
        Timer = Stopwatch.StartNew(),
        OriginalValue = input
    };
}
```

## Private Field Access: `___fieldName`

Access private fields using three underscores + field name:

```csharp
[HarmonyPatch(typeof(MyClass), nameof(MyClass.DoWork))]
static class FieldAccessPatch
{
    // Reading a private field
    static void Prefix(int ___m_counter)
    {
        Log.Info($"Counter is: {___m_counter}");
    }

    // Modifying a private field
    static void Postfix(ref int ___m_counter)
    {
        ___m_counter++;
    }
}
```

The field name is the parameter name without the leading `___`. Harmony searches the type hierarchy.

## All Arguments: `__args`

Access all arguments as an `object[]`:

```csharp
static void Prefix(object[] __args)
{
    Log.Info($"Called with {__args.Length} arguments");
    for (int i = 0; i < __args.Length; i++)
        Log.Info($"  [{i}] = {__args[i]}");
}
```

You can modify values in the array to change arguments:

```csharp
static void Prefix(object[] __args)
{
    __args[0] = "modified value"; // Changes first argument
}
```

**Performance note:** This has slight overhead compared to named parameters.

## Original Method Info: `__originalMethod`

Get the `MethodBase` of the patched method:

```csharp
static void Prefix(MethodBase __originalMethod)
{
    Log.Info($"Patching: {__originalMethod.DeclaringType}.{__originalMethod.Name}");
}
```

Useful when applying the same patch to multiple methods via `TargetMethods()`.

## Execution Status: `__runOriginal`

Check if the original method will run (prefix) or did run (postfix):

```csharp
static void Postfix(bool __runOriginal, int __result)
{
    if (__runOriginal)
        Log.Info($"Original ran, returned: {__result}");
    else
        Log.Info("Original was skipped by a prefix");
}
```

## Method Arguments by Name

Match parameter names to access arguments:

```csharp
// Original: void Attack(Entity target, float damage, bool critical)
static void Prefix(Entity target, float damage)
{
    Log.Info($"Attacking {target.Name} for {damage} damage");
}
```

To modify arguments, use `ref`:

```csharp
static void Prefix(ref float damage, bool critical)
{
    if (critical)
        damage *= 2f;
}
```

### Using Index When Names Conflict

If a parameter name conflicts with a reserved injection, use `__n` notation:

```csharp
// Original has a parameter named "instance"
static void Prefix(
    [HarmonyArgument("instance")] Entity target,  // Attribute approach
    Entity __0)  // Or: use index (0 = first argument)
{
}
```

## Ref Return Values: `__resultRef`

For methods with `ref` returns, use `RefResult<T>`:

```csharp
// Original: ref int GetValue()
static void Postfix(ref RefResult<int> __resultRef)
{
    // Modify what the ref points to
    __resultRef.Value = 42;
}
```

## Transpiler-Specific Injections

Transpilers match by type, not name:

```csharp
static IEnumerable<CodeInstruction> Transpiler(
    IEnumerable<CodeInstruction> instructions,  // Required: original IL
    ILGenerator generator,                       // Optional: for creating labels/locals
    MethodBase original)                         // Optional: method info
{
    // ...
}
```

## Combining Injections

You can use multiple injections together:

```csharp
static void Prefix(
    MyClass __instance,           // The instance
    ref int __result,             // Return value (will set)
    int ___m_health,              // Private field
    string targetName,            // Method argument
    MethodBase __originalMethod)  // Reflection info
{
    Log.Info($"[{__originalMethod.Name}] {__instance} attacking {targetName}, health={___m_health}");
}
```

## See Also

- [Patching.md](Patching.md) - Basic patch structure
- [AccessTools.md](AccessTools.md) - Finding methods and fields for patching
