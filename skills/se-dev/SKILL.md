---
name: se-dev
description: High level overview of Space Engineers (version 1) related development. Start here to understand the ecosystem (game client, dedicated server, Pulsar, Magnetar, Torch, PluginHub, MagnetarHub, Quasar) and to route to the right se-dev-* skill for in-game scripts, mods, plugins, the Magnetar PluginSdk, and decompiled code/handbook reference.
license: MIT
allowed-tools: Read
---

# SE Dev — Space Engineers Development Overview

**Applies only to Space Engineers version 1.**

Entry point and table of contents for `se-dev-*` skills. Read this first to get
big picture, then open specific skill the task needs. Does not perform searches or builds
itself — routes you to the skill that does.

## The three ways to extend the game

| Layer | What it is | Runs as | Language limit | Skill |
|-------|-----------|---------|----------------|-------|
| **In-game script** | Code in Programmable Block (PB) | Sandboxed, compiled by game | C# 6.0, PB API whitelist | [`se-dev-script`](../se-dev-script/SKILL.md) |
| **Mod** | World/server content & scripts, Steam Workshop | Sandboxed, compiled by game | C# 7.3, Mod API whitelist | [`se-dev-mod`](../se-dev-mod/SKILL.md) |
| **Plugin** | Native DLL patching game with Harmony | Unsandboxed, full .NET | No limit (`latestMinor`) | [`se-dev-plugin`](../se-dev-plugin/SKILL.md) |

Scripts and mods constrained by API whitelists and run inside game's sandbox. Plugins run native
code with no sandbox — can do anything, which is why they are open source and reviewed before release.

## Where plugins run: client vs server

A plugin targets the **game client**, the **dedicated server**, or both (sharing code).

| | Game client | Dedicated server | Torch (legacy) |
|---|---|---|---|
| **Loader** | Pulsar | Magnetar | Torch |
| **Registry** | PluginHub | MagnetarHub | torchapi.net |
| **Admin UI** | in-game config dialog | [Quasar](https://github.com/CometWorks/quasar) (remote control plane) | Torch WPF UI |
| **Skill** | `se-dev-plugin` (`ClientPlugin`) | `se-dev-plugin` (`ServerPlugin`) + `se-dev-plugin-sdk` | `se-dev-torch` |

- **[Pulsar](https://github.com/SpaceGT/Pulsar)** — plugin & mod loader for game client. Lists and loads plugins from **[PluginHub](https://github.com/StarCpt/PluginHub/)**. Compiles client plugins from source on player's machine.
- **[Magnetar](https://magnetar.se)** — plugin loader for dedicated server (hard fork of Pulsar). Lists and loads server plugins from **[MagnetarHub](https://github.com/CometWorks/magnetar-hub)**. Server plugins declare their configuration through Magnetar's **PluginSdk**.
- **[Quasar](https://github.com/CometWorks/quasar)** — control plane with Web UI to manage Magnetar instances. Lists Magnetar-compatible server plugins from MagnetarHub and lets admins configure them remotely; configuration UI is the layout each plugin declares via PluginSdk.
- **[Torch](https://torchapi.com/)** — older, separate dedicated-server host with its own plugin model. **Torch plugins not compatible with Magnetar and vice versa.** Covered only by `se-dev-torch` / `se-dev-torch-book` skills, kept for maintaining existing Torch plugins.

## Skill map

### Authoring skills (write scripts, mods, plugins)
- **[se-dev-script](../se-dev-script/SKILL.md)** — In-game (Programmable Block) script development. Search example PB scripts.
- **[se-dev-mod](../se-dev-mod/SKILL.md)** — Mod development. Search example mod code; Mod API whitelist.
- **[se-dev-plugin](../se-dev-plugin/SKILL.md)** — Client and server plugin development (Harmony patching, transpilers, preloader). Search plugin source from PluginHub.
- **[se-dev-plugin-sdk](https://github.com/CometWorks/magnetar/tree/main/skills/se-dev-plugin-sdk)** — Handbook for Magnetar's PluginSdk: declaring server config variables, UI layout Quasar renders, server-side chat commands, server lifecycle (save/reload/quit/restart), path resolution and environment-agnostic logging. Use together with `se-dev-plugin` for server plugins. *(Lives in [Magnetar](https://github.com/CometWorks/magnetar) repo.)*
- **[se-dev-torch](../se-dev-torch/SKILL.md)** — Torch plugin development (legacy server host). Torch-only; not Magnetar-compatible.

### Reference skills (read/search the game internals)
- **[se-dev-game-code](../se-dev-game-code/SKILL.md)** — Search decompiled C# of game **client**. Recommended companion for client mod/plugin work.
- **[se-dev-server-code](../se-dev-server-code/SKILL.md)** — Search decompiled C# of **dedicated server**. Companion for server-side mod/plugin work.

## How to pick

- **Programmable Block script?** → `se-dev-script` (+ `se-dev-game-code` / `se-dev-game-book` for API details).
- **Steam Workshop mod?** → `se-dev-mod` (+ `se-dev-game-code` / `se-dev-server-code` as needed).
- **Client plugin?** → `se-dev-plugin` + `se-dev-game-code` (and `se-dev-game-book` for orientation).
- **Server plugin (Magnetar)?** → `se-dev-plugin` + `se-dev-plugin-sdk` + `se-dev-server-code` (and `se-dev-server-book`).
- **Maintaining a Torch plugin?** → `se-dev-torch` + `se-dev-torch-book` (and `se-dev-server-code`).
- **Need to understand how the game does X?** → `*-code` skills to search source, `*-book` skills for orientation.

Most non-trivial tasks pair an **authoring** skill with a **reference** skill: write with one, look up game's
internals with the other.

## Plugin templates

- [se-client-plugin-template](https://github.com/CometWorks/client-plugin-template) — client-only plugin.
- [se-server-plugin-template](https://github.com/CometWorks/server-plugin-template) — client + Magnetar server plugin (`ClientPlugin`, `ServerPlugin`, `Shared`). For **Torch** plugin, base it on template's `last-torch-compatible` tag, not `main`.

## Remarks

Original source of these skills: https://github.com/viktor-ferenczi/se-dev-skills
