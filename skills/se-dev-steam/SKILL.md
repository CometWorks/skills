---
name: se-dev-steam
description: Space Engineers version 1 Steam integration.
license: MIT
allowed-tools: Read
---

# SE Dev Steam Skill

Reference information on Space Engineers Steam integration, workshop content, and blueprint management.

Steam App ID 244850, Steam Workshop URLs, steamcmd CLI for downloading blueprints and mods,
workshop content paths on disk, blueprint bp.sbc files, ProjectedGrids cleaning,
and Steam IDs in save games.
Use this skill whenever the user asks about SE Steam Workshop, downloading blueprints or mods
from Steam, steamcmd commands, workshop item IDs, or Steam content file locations.

## Key Identifiers

- **Space Engineers App ID**: `244850`
- **Steam Workshop URL**: `https://steamcommunity.com/sharedfiles/filedetails/?id=<ITEM_ID>`
- **Steam Store URL**: `https://store.steampowered.com/app/244850/Space_Engineers/`

## Steam Workshop Content Paths

Downloaded workshop content (mods and blueprints) is stored in:

### Steam Client (players)

| Platform | Path |
|----------|------|
| Windows | `C:\Program Files (x86)\Steam\steamapps\workshop\content\244850\<item_id>\` |
| Linux | `~/.steam/steamapps/workshop/content/244850/<item_id>/` |

### Dedicated Server (steamcmd)

| Platform | Path |
|----------|------|
| Windows | `C:\SEServer\steamcmd\steamapps\workshop\content\244850\<item_id>\` |
| Linux | `~/.steam/steamapps/workshop/content/244850/<item_id>/` |

The `<item_id>` folder contains the mod or blueprint files. For blueprints the key file is `bp.sbc`.

### How to Determine the Actual Path

The Steam installation directory varies. To find it:
- **Windows**: Check the registry key `HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam\InstallPath` or look in common locations (`C:\Program Files (x86)\Steam`, `D:\Steam`, etc.)
- **Linux**: Usually `~/.steam` or `~/.local/share/Steam`
- **steamcmd**: The content directory is relative to where steamcmd is installed

## Downloading Blueprints with steamcmd

### Command

```bash
steamcmd +login anonymous +workshop_download_item 244850 <ITEM_ID> +quit
```

This downloads the workshop item using anonymous authentication (no Steam account needed for public items).

### steamcmd Location

| Platform | Default Path |
|----------|-------------|
| Windows | `C:\SEServer\steamcmd\steamcmd.exe` |
| Linux | `/usr/games/steamcmd` (install via `apt install steamcmd`) |

### Downloaded Blueprint Path

After download, the blueprint file is at:

```
<steamcmd_content_dir>/244850/<ITEM_ID>/bp.sbc
```

For example on Linux: `~/.steam/steamapps/workshop/content/244850/2306903082/bp.sbc`

### Blueprint Downloader Reference

A production blueprint download service exists at:
`C:\Dev\SE1\space_battle\tools\blueprint_downloader.py`

It implements a request/response folder-based workflow:
1. A request file containing a Steam Workshop URL or numeric ID is placed in `~/.cache/blueprint_downloader/requests/`
2. The downloader polls for requests, downloads via steamcmd, cleans the blueprint, and places the result in `~/.cache/blueprint_downloader/responses/`
3. Downloads are cached for 24 hours
4. Designed to run as a periodic cron job (every 10 minutes)

Features:
- Supports both Steam Workshop downloads and direct HTTP/HTTPS URLs
- Cleans blueprints by filtering deeply nested ProjectedGrids (see below)
- 60-second timeout for steamcmd downloads
- 10 MB size limit for URL downloads

## Blueprint Cleaning

### The ProjectedGrids Problem

Blueprints can contain `<ProjectedGrids>` elements representing projector blocks that project other blueprints. These can be recursively nested (a projection containing a projection containing a projection...), creating extremely large files that cause performance issues.

### Cleaning Strategy

Filter ProjectedGrids by nesting depth using a SAX-based XML parser. The typical maximum useful depth is 2 levels. Content beyond this depth is stripped out.

The `BlueprintCleaner` class in `scripts/blueprint_downloader.py` implements this:
- Tracks a `projection_depth` counter
- Increments on `<ProjectedGrids>` open, decrements on close
- Suppresses all XML output when depth exceeds the limit
- SAX-based approach is memory-efficient for large blueprint files

A standalone cleaner tool is also available at: `scripts/blueprint_cleaner.py`

## Steam IDs in Save Games

Steam IDs are 64-bit integers that appear in save game files for:

- **Admin accounts**: `<Administrators><unsignedLong>STEAM_ID</unsignedLong></Administrators>`
- **Promoted users**: `<PromotedUsers>` dictionary mapping Steam ID to permission level
- **Player identities**: Linking Steam accounts to in-game IdentityId values
- **Client entries**: `<MyObjectBuilder_Client>` with `<SteamId>`, `<Name>`, `<IsAdmin>`
- **Grid/block ownership**: Indirectly, through IdentityId which maps to a Steam ID

## Remarks

The original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
