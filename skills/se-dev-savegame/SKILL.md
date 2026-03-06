---
name: se-dev-savegame
description: Space Engineers version 1 save game file structure and editing.
license: MIT
allowed-tools: Read
---

# SE Dev Savegame Skill

Reference information on Space Engineers save game file structure and editing.

How to read and modify Sandbox.sbc and Sandbox_config.sbc XML files.
Changing mods by editing the Mods element, copying mods between saves,
understanding the sector file (SANDBOX_0_0_0_.sbs) with grids and blocks.
Use this skill whenever the user asks about SE save game files, world editing,
mod lists in saves, or programmatic save game manipulation.

## Save Game Folder Structure

A save game (world) folder contains:

```
WorldName/
  Sandbox.sbc                    Main session configuration (XML)
  Sandbox_config.sbc             Configuration variant (XML, must stay in sync)
  SANDBOX_0_0_0_.sbs             Sector objects: grids, safe zones, voxels (XML)
  SpaceEngineers-Dedicated.cfg   Dedicated server configuration (only on servers)
  *.vx2                          Asteroid/voxel data (binary, not text-editable)
```

Save game locations:
- **Single player / local**: `%AppData%\SpaceEngineers\Saves\<SteamId>\<WorldName>\`
- **Dedicated server**: Configured in the server's instance directory

## Sandbox.sbc

The main session configuration file. Key elements:

| Element | Purpose |
|---------|---------|
| `<SessionName>` | World name displayed in the game |
| `<Settings>` | Game settings (game mode, world size, block limits, etc.) |
| `<Mods>` | List of Steam Workshop mods enabled in this world |
| `<Identities>` | Player identities (IdentityId, DisplayName, SteamId) |
| `<Factions>` | Faction definitions and membership |
| `<Gps>` | GPS markers organized by player IdentityId |
| `<PromotedUsers>` | Admin and promoted user Steam IDs |
| `<SessionComponents>` | Game systems (safe zones, banking, store, etc.) |

## Sandbox_config.sbc

A configuration variant that also contains `<Settings>` and `<Mods>`. When editing mods or settings you must update both Sandbox.sbc and Sandbox_config.sbc to keep them in sync. Failing to update both files leads to inconsistencies and potential crashes.

## SANDBOX_0_0_0_.sbs

The sector file containing all world objects under `<SectorObjects>`:

- **Grids** (ships, stations) with `<CubeBlocks>` defining individual blocks
- **Safe zones** with access control configuration
- **Voxels** (asteroid/planet metadata, binary data stored in .vx2 files)
- **Floating objects** and **characters**

Each entity has a unique `<EntityId>` (64-bit integer).

## Editing Mods in Save Games

### ModItem XML Structure

Both Sandbox.sbc and Sandbox_config.sbc contain a `<Mods>` element with `<ModItem>` children:

```xml
<Mods>
  <ModItem FriendlyName="Text HUD API">
    <Name>758597413.sbm</Name>
    <PublishedFileId>758597413</PublishedFileId>
    <IsDependency>true</IsDependency>
  </ModItem>
  <ModItem FriendlyName="Build Vision 2.5">
    <Name>1697184408.sbm</Name>
    <PublishedFileId>1697184408</PublishedFileId>
  </ModItem>
</Mods>
```

Fields:
- `FriendlyName` attribute: The mod's display name
- `<Name>`: The mod file name, formatted as `<PublishedFileId>.sbm`
- `<PublishedFileId>`: The Steam Workshop item ID
- `<IsDependency>`: Optional, `true` if the mod is an automatic dependency of another mod

### Edit BOTH Files

When modifying mods you must update `<Mods>` in both:
1. **Sandbox.sbc**
2. **Sandbox_config.sbc**

### Adding a Mod

Insert a new `<ModItem>` element inside `<Mods>` in both files:

```xml
<ModItem FriendlyName="Your Mod Name">
  <Name>WORKSHOP_ID.sbm</Name>
  <PublishedFileId>WORKSHOP_ID</PublishedFileId>
</ModItem>
```

Replace `WORKSHOP_ID` with the Steam Workshop item ID and `Your Mod Name` with the mod's display name.

### Removing a Mod

Find and delete the matching `<ModItem>` element from both files.

### Removing All Mods

Clear all `<ModItem>` children from the `<Mods>` element in both files, leaving an empty `<Mods />` element.

## Copying Mods Between Saves

To copy the mod list from one save to another:

1. Open the **source** save's Sandbox.sbc
2. Copy the entire `<Mods>...</Mods>` element
3. Open the **target** save's Sandbox.sbc
4. Replace the entire `<Mods>...</Mods>` element with the copied one
5. Repeat steps 1-4 for Sandbox_config.sbc

This ensures the target save uses the exact same mod set as the source.

## Programmatic Save Game Editing

For Python-based save game editing, see the `se_tool` package at:
`C:\Dev\SE1\space_battle\tools\setool`

This is a private tool (never released publicly) designed for multiplayer scenario preparation. It uses `lxml` for XML processing and demonstrates patterns for:

- Reading/writing SE XML files (`xml_utils.py`: `read_xml`, `write_xml`, `process_xml`)
- Context manager for atomic read-modify-write (`World.process()`)
- Managing identities and factions
- Manipulating grids and blocks (ownership, custom data, components)
- Working with GPS coordinates and 3D vectors
- Safe zone configuration
- Mod removal across both config files

Key entry point: `world.py` contains the `World` class with methods for all save game operations.

## Remarks

The original source of this skill: https://github.com/viktor-ferenczi/se-dev-skills
