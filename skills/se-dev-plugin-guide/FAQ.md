# FAQ

**Which C# version can I use?** C# 14; Pulsar compiles with it. Set `LangVersion` to `latestMinor` or 14.
Mods are limited to C# 7.3 and PB scripts to C# 6, because the game compiles those itself.

**Can I use NuGet packages?** Yes, declared in `NuGetReferences`. For the Legacy flavor they need
`net48` or `netstandard2.0`; `netstandard2.0` works on both flavors.

**Can I bring data files?** Yes, as assets. Implement `LoadAssets` in your `Plugin` class.

**Can I develop on Linux?** Yes, with Pulsar's native Linux build. See [Linux](LocalTesting.md#linux).

**How do I register a Workshop mod?** See the end of [Submit to the hub](Submitting.md).
