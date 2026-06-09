# Quick Start

Use this file when you need to get moving inside Torch quickly.

## 1. Prepare the skill

If you already have local checkout:

```bash
TORCH_ROOT=/path/to/Torch ./Prepare.sh
```

If not, run:

```bash
./Prepare.sh
```

Preparation writes chosen source root to `Data/torch_root.txt` and builds code index under `Data/CodeIndex`.

## 2. Start with the right source area

- Plugin lifecycle and metadata:
  Read [TorchPlugin.md](TorchPlugin.md)
- Source tree map:
  Read [Architecture.md](Architecture.md)
- Search syntax and filters:
  Read [CodeSearch.md](CodeSearch.md)

## 3. First searches

```bash
uv run search_torch.py class declaration TorchPluginBase
uv run search_torch.py interface declaration ITorchPlugin -n Torch.API.Plugins
uv run search_torch.py class declaration PluginManager -n Torch.Managers
uv run search_torch.py class declaration CommandManager -n Torch.Commands
uv run search_torch.py interface declaration ITorchSessionManager -n Torch.API.Session
```

## 4. Match searches to the task

- New plugin class:
  Search `TorchPluginBase`, `ITorchPlugin`, and `PluginManifest`
- Command handling:
  Search `CommandModule`, `CommandAttribute`, and `RegisterPluginCommands`
- Session or global managers:
  Search `DependencyManager`, `ITorchSessionManager`, and `Manager`
- WPF server controls:
  Search `IWpfPlugin`, then inspect `Torch.Server/Views` and `Torch/ViewModels`
- Patching:
  Search `PatchManager`, `PatchContext`, and the `Torch.Managers.PatchManager` namespace

## 5. When Torch is not enough

Torch explains framework side. For Keen classes, game events, or dedicated server internals, pair this with:

- `se-dev-game-code`
- `se-dev-server-code`
