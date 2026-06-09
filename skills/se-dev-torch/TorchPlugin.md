# Torch Plugin Development

This file covers Torch-specific authoring model. Read [Architecture.md](Architecture.md) after this when you need deeper implementation details.

> **Compatibility:** Plugins developed according to this guide are compatible **only with Torch**, not with [Magnetar](https://magnetar.se). Torch and Magnetar are different dedicated-server hosts with different patcher and SDK — Torch plugin will not load into Magnetar, and Magnetar plugin will not load into Torch. For Magnetar server plugins use `se-dev-plugin` and `se-dev-plugin-sdk` skills instead.
>
> If you base Torch plugin on [se-server-plugin-template](https://github.com/viktor-ferenczi/se-server-plugin-template), check out **`last-torch-compatible`** tag as starting point — current `main` branch dropped Torch target and now targets Magnetar:
>
> ```bash
> git clone https://github.com/viktor-ferenczi/se-server-plugin-template
> cd se-server-plugin-template
> git checkout last-torch-compatible
> ```

## Start with the current plugin model

Use these source files first:

- `Torch.API/Plugins/ITorchPlugin.cs`
- `Torch.API/Plugins/IWpfPlugin.cs`
- `Torch/TorchPluginBase.cs`
- `Torch/Plugins/PluginManifest.cs`
- `Torch/Plugins/PluginManager.cs`

## Metadata and loading

Torch loads plugins through `manifest.xml`, not through `[PluginAttribute]`.

Important points:

- `manifest.xml` is current metadata source
- `PluginAttribute` is marked obsolete
- `PluginManifest` contains `Name`, `Guid`, `Version`, and `Dependencies`
- `PluginManager` looks for `manifest.xml` in plugin folders or zip files

When answering plugin packaging questions, treat `manifest.xml` as authoritative.

## Base class and lifecycle

`TorchPluginBase` is normal base class.

Key members:

- `Init(ITorchBase torch)` sets Torch instance
- `Update()` runs after each tick
- `Dispose()` handles cleanup
- `IsReloadable` controls whether plugin can be reloaded
- `Manifest`, `Name`, `Id`, and `Version` come from loaded manifest

Use `ITorchPlugin` only when task clearly needs lower-level interface.

## Getting managers

Prefer dependency manager APIs over obsolete convenience helpers.

Use:

- `torch.Managers.GetManager<T>()` for global managers
- `torch.CurrentSession?.Managers.GetManager<T>()` for session-scoped managers

Avoid relying on obsolete `ITorchBase.GetManager<T>()` unless explaining old code.

Relevant source files:

- `Torch.API/ITorchBase.cs`
- `Torch.API/Managers/IManager.cs`
- `Torch/Managers/Manager.cs`
- `Torch/Managers/DependencyManager.cs`
- `Torch.API/Session/ITorchSessionManager.cs`

## Commands

Torch commands are centered on:

- `Torch/Commands/CommandModule.cs`
- `Torch/Commands/CommandAttribute.cs`
- `Torch/Commands/CommandManager.cs`
- `Torch/Commands/CommandContext.cs`

Patterns:

- Put command methods on class derived from `CommandModule`
- Mark methods with `[Command("path subcommand")]`
- Use `Context` for command execution context
- Plugin command registration happens through `PluginManager` when session loads

Search for `RegisterPluginCommands` and `UnregisterPluginCommands` to inspect exact registration flow.

## Session managers

Torch distinguishes between:

- Global managers attached to Torch instance
- Session managers created per running game session

`ITorchSessionManager.AddFactory(...)` is entry point for registering factories that create session-scoped managers.

Use this area when task needs behavior that follows world/session lifecycle rather than application startup.

## WPF server UI

If plugin exposes Torch server UI control, implement `IWpfPlugin`.

Key point:

- `GetControl()` must instantiate control on correct WPF thread

Inspect these areas for examples:

- `Torch.API/Plugins/IWpfPlugin.cs`
- `Torch.Server/Views/`
- `Torch/ViewModels/`

## Patching

Torch has its own patch manager infrastructure under `Torch/Managers/PatchManager/`.

Read [Architecture.md](Architecture.md) and search:

```bash
uv run search_torch.py namespace declaration PatchManager
uv run search_torch.py class declaration PatchContext -n Torch.Managers.PatchManager
uv run search_torch.py class declaration PatchShimAttribute -n Torch.Managers.PatchManager
```

Do not assume Harmony-only patterns from other plugin ecosystems map directly onto Torch internals without checking source.
