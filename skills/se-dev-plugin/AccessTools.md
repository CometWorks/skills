# AccessTools for Reflection

`AccessTools` is Harmony's utility class for reflection. Use it to find private fields, methods, properties, and types when writing patches.

## When to Use AccessTools

Use `AccessTools` when you need to:
- Access private/internal fields or properties in patch code
- Get a `MethodInfo` for dynamic patching via `TargetMethod()`
- Find nested/inner types that aren't publicly accessible
- Create delegates for efficient repeated field access

## Common Patterns

### Finding Methods

```csharp
// Find a method by name (searches base types too)
var method = AccessTools.Method(typeof(SomeClass), "MethodName");

// Find an overloaded method by parameter types
var method = AccessTools.Method(typeof(SomeClass), "MethodName", new[] { typeof(int), typeof(string) });

// Find a generic method
var method = AccessTools.Method(typeof(SomeClass), "GenericMethod", null, new[] { typeof(MyType) });

// Shorthand: "Namespace.Class:Method" syntax
var method = AccessTools.Method("Sandbox.Game.MyClass:MyMethod");
```

### Finding Fields and Properties

```csharp
// Find a private field (searches base types)
var field = AccessTools.Field(typeof(SomeClass), "m_privateField");

// Find a property
var prop = AccessTools.Property(typeof(SomeClass), "SomeProperty");

// Get the getter/setter MethodInfo
var getter = AccessTools.PropertyGetter(typeof(SomeClass), "SomeProperty");
var setter = AccessTools.PropertySetter(typeof(SomeClass), "SomeProperty");
```

### Finding Constructors

```csharp
// Find a constructor by parameter types
var ctor = AccessTools.Constructor(typeof(SomeClass), new[] { typeof(int) });

// Find the static constructor
var cctor = AccessTools.Constructor(typeof(SomeClass), null, searchForStatic: true);
```

### Finding Types

```csharp
// Find a type by full name
var type = AccessTools.TypeByName("Sandbox.Game.SomeNamespace.SomeClass");

// Find a nested/inner type
var innerType = AccessTools.Inner(typeof(OuterClass), "InnerClassName");
```

## Using AccessTools in Patches

### Dynamic Target Method

Use `TargetMethod()` when you can't use attributes (e.g., the type is private):

```csharp
[HarmonyPatch]
static class MyPatch
{
    static MethodBase TargetMethod()
    {
        // Find a method inside a private nested class
        var type = AccessTools.Inner(typeof(SomePublicClass), "PrivateNestedClass");
        return AccessTools.Method(type, "SomeMethod");
    }

    static void Prefix() { /* ... */ }
}
```

### Multiple Target Methods

Apply the same patch to multiple methods:

```csharp
[HarmonyPatch]
static class MultiPatch
{
    static IEnumerable<MethodBase> TargetMethods()
    {
        yield return AccessTools.Method(typeof(ClassA), "DoThing");
        yield return AccessTools.Method(typeof(ClassB), "DoThing");
        yield return AccessTools.Method(typeof(ClassC), "DoThing");
    }

    static void Postfix() { /* runs after any of these methods */ }
}
```

### Efficient Field Access via Delegates

For repeated field access (e.g., in a frequently called patch), create delegates once:

```csharp
static class MyPatch
{
    // Create delegate once, reuse in patches
    static readonly AccessTools.FieldRef<MyClass, int> CounterRef =
        AccessTools.FieldRefAccess<MyClass, int>("m_counter");

    static void Postfix(MyClass __instance)
    {
        // Fast field access without reflection overhead
        int value = CounterRef(__instance);
        CounterRef(__instance) = value + 1;
    }
}
```

For static fields:

```csharp
static readonly ref int StaticCounter =
    ref AccessTools.StaticFieldRefAccess<int>(typeof(MyClass), "s_counter");
```

## Declared vs. Regular Methods

- `AccessTools.Method()` - searches the type **and all base types**
- `AccessTools.DeclaredMethod()` - searches **only the specified type**

Use the `Declared*` variants when you specifically need a member from a particular type level, not inherited ones:

```csharp
// Gets the method even if defined in a base class
var inherited = AccessTools.Method(typeof(DerivedClass), "SomeMethod");

// Only finds it if DerivedClass itself declares it
var declared = AccessTools.DeclaredMethod(typeof(DerivedClass), "SomeMethod");
```

## Bulk Discovery

When exploring a type's members:

```csharp
// Get all fields declared on a type
List<FieldInfo> fields = AccessTools.GetDeclaredFields(typeof(SomeClass));

// Get all methods declared on a type
List<MethodInfo> methods = AccessTools.GetDeclaredMethods(typeof(SomeClass));

// Get all member names
List<string> fieldNames = AccessTools.GetFieldNames(typeof(SomeClass));
List<string> methodNames = AccessTools.GetMethodNames(typeof(SomeClass));
```

## Creating Instances

```csharp
// Create an instance (may be uninitialized for some types)
var instance = AccessTools.CreateInstance<SomeClass>();
var instance2 = AccessTools.CreateInstance(typeof(SomeClass));
```

## Tips for Space Engineers Plugins

1. **Use the game code search** (`se-dev-game-code` skill) to find exact field/method names before using `AccessTools`
2. **Prefer `AccessTools` over raw reflection** - it handles edge cases and searches base types automatically
3. **Cache reflection results** - store `MethodInfo`/`FieldInfo` in static fields, don't look them up repeatedly
4. **Use `FieldRefAccess` for hot paths** - avoids reflection overhead in frequently called code
5. **Check for null returns** - `AccessTools` methods return `null` if the member isn't found rather than throwing

## See Also

- [Patching.md](Patching.md) - Basic Harmony patching
- [PatchInjections.md](PatchInjections.md) - Special parameters in patch methods
- [TranspilerPatching.md](TranspilerPatching.md) - IL-level patching
