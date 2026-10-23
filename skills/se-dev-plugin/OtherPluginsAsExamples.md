# Looking at Other Plugins as Examples

Look into the source code of any other plugin registered on the `PluginHub` as examples, all open source.

## Finding and Downloading Plugins

### Step 1: List Available Plugins

```bash
# List all plugins
uv run list_plugins.py

# Search for plugins by keyword
uv run list_plugins.py --search "camera"
uv run list_plugins.py --search "paint"
uv run list_plugins.py --search "tool"
```

### Step 2: Download Plugin Source

**IMPORTANT**: Use the EXACT plugin name, ID or `Owner/Repo` as shown in the list output.

```bash
# ✅ CORRECT - exact name, ID or Owner/Repo (matching ignores case)
uv run download_plugin_source.py "Paint Replacer"
uv run download_plugin_source.py "Tool Switcher"
uv run download_plugin_source.py viktor-ferenczi/se-paint-replacer

# ❌ WRONG - a term that is not an exact match falls back to a substring match
uv run download_plugin_source.py "PaintReplacer"   # no match: fails
uv run download_plugin_source.py "Paint"           # several matches: lists them and fails
```

**Tip**: Copy-paste the name directly from `list_plugins.py` output to avoid typos.

### Step 3: Search Downloaded Plugin Code

After downloading, the plugin is automatically indexed and ready to search:

```bash
# Search across all downloaded plugins
uv run search_plugins.py class declaration Plugin
uv run search_plugins.py method signature Patch
```

## Manual Plugin Discovery (Alternative Method)

Look into the `Data/PluginHub` (client) and `Data/MagnetarHub` (server) folders next to this skill file. Each has a `Plugins`
subdirectory with XML files in it.

Find the right plugins to look into by searching in the XML files in the `Data/PluginHub/Plugins` and `Data/MagnetarHub/Plugins` folders.
They have `FriendlyName` and `Description` which should be enough to identify what they are about in most cases.
The `DotNetCompat` plugin is special (internal plugin), only use it if you want good examples for preloader patches.

Each XML file corresponds to a plugin registered on the PluginHub. The `<RepoId>` (or if not present,
then the `Id`) field tells you the GitHub repository ID of the plugin. 

## Plugin Storage

`download_plugin_source.py` clones plugin sources into `Data/Sources/<RepoName>/` and checks out the
commit the registry pins. `Data` links to the per-user skill data folder (`~/.se-dev/plugin` on Linux,
`%USERPROFILE%\.se-dev\plugin` on Windows), created by preparation.

## Examples of Finding Plugins

### Example 1: Find Camera-Related Plugins
```bash
$ uv run list_plugins.py --search "camera"
Found 2 plugins (0 available locally)

[REMOTE] [PluginHub] Camera Panning
  ID: avaness/CameraPanning
  Author: avaness

[REMOTE] [PluginHub] Free Camera
  ID: carlosmaid/FreeCameraPlus
  Author: carlosmaid

# Download exact name
$ uv run download_plugin_source.py "Camera Panning"
```

### Example 2: Find All Tool-Related Plugins
```bash
$ uv run list_plugins.py --search "tool"
Found 3 plugins (0 available locally)

[REMOTE] [PluginHub] Tool Switcher
  ID: austinvaness/ToolSwitcherPlugin
  Author: austinvaness

[REMOTE] [PluginHub] Server Tools
  ID: rexxar-tc/ServerTools
  Author: Rexxar

# Download the one you want (use EXACT name)
$ uv run download_plugin_source.py "Tool Switcher"
```

## Re-indexing

The `download_plugin_source.py` script automatically re-indexes all downloaded plugins. 

If you manually add/remove plugin sources, re-index with:
```bash
uv run index_plugins.py
```