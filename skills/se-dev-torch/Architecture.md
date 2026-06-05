# Torch Architecture Map

Use this file to choose the right source area before reading individual files.

## Main source roots

| Area | Source root | Purpose |
|------|-------------|---------|
| Public API | `Torch.API/` | Interfaces and contracts intended for plugins |
| Core implementation | `Torch/` | Plugin manager, command system, managers, patches, shared UI |
| Dedicated server host | `Torch.Server/` | Server bootstrap, WPF host UI, server-side managers |
| In-game bridge mod | `Torch.Mod/` | Mod-side communication and message types |
| Tests | `Torch.Client.Tests/` | Small amount of behavior verification |

## Start here by topic

### Plugin lifecycle and metadata

- `Torch.API/Plugins/ITorchPlugin.cs`
- `Torch.API/Plugins/IWpfPlugin.cs`
- `Torch/TorchPluginBase.cs`
- `Torch/Plugins/PluginManifest.cs`
- `Torch/Plugins/PluginManager.cs`

### Torch instance and managers

- `Torch.API/ITorchBase.cs`
- `Torch.API/Managers/`
- `Torch.API/Session/`
- `Torch/Managers/Manager.cs`
- `Torch/Managers/DependencyManager.cs`
- `Torch/Session/TorchSessionManager.cs`

### Commands

- `Torch/Commands/CommandModule.cs`
- `Torch/Commands/CommandAttribute.cs`
- `Torch/Commands/CommandManager.cs`
- `Torch/Commands/CommandContext.cs`

### Patching

- `Torch/Managers/PatchManager/`
- `Torch/Patches/`

### Server UI and controls

- `Torch.Server/Views/`
- `Torch.Server/ViewModels/`
- `Torch/Views/`
- `Torch/ViewModels/`

### Plugin update and registry integration

- `Torch.API/WebAPI/`
- `Torch/Plugins/PluginManager.cs`

## High-value search anchors

Use these when you need an entry point fast:

```bash
uv run search_torch.py class declaration TorchBase
uv run search_torch.py class declaration PluginManager
uv run search_torch.py class declaration CommandManager
uv run search_torch.py class declaration DependencyManager
uv run search_torch.py interface declaration ITorchSessionManager
uv run search_torch.py namespace declaration PatchManager
```

## Important conventions

- `manifest.xml` is the active plugin metadata model
- `PluginAttribute` exists but is obsolete
- `ITorchBase.GetManager<T>()` is obsolete; prefer `Managers.GetManager<T>()`
- Session-specific functionality often hangs off `ITorchSessionManager` and `ITorchSession`

## When to leave this skill

If the answer depends on Keen engine behavior rather than Torch framework behavior, switch to:

- `se-dev-game-code`
- `se-dev-server-code`
