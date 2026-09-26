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
- **[se-dev-plugin-review](../se-dev-plugin-review/SKILL.md)** — Review PluginHub, MagnetarHub, and QuasarHub PRs from their manifest pins; produces concise paste-ready findings while reserving approval for a human maintainer.
- **[se-dev-plugin-sdk](https://github.com/CometWorks/magnetar/tree/main/skills/se-dev-plugin-sdk)** — Handbook for Magnetar's PluginSdk: declaring server config variables, UI layout Quasar renders, server-side chat commands, server lifecycle (save/reload/quit/restart), path resolution and environment-agnostic logging. Use together with `se-dev-plugin` for server plugins. *(Lives in [Magnetar](https://github.com/CometWorks/magnetar) repo.)*
- **[se-dev-torch](../se-dev-torch/SKILL.md)** — Torch plugin development (legacy server host). Torch-only; not Magnetar-compatible.

### Graphify graphs (read on demand)
- **[GraphifyPrepare.md](GraphifyPrepare.md)** — how each subskill builds its own per-subskill `graphify-out/`. Prepare installs Graphify on **Python 3.12 with the fast native Rust Leiden clustering backend** and, when that backend is available (Linux/Windows with `uv`), builds the graph **automatically** — clustering then takes ~1-2 minutes even for the game/server corpora. Where the fast backend cannot be provisioned, Graphify stays **optional** and only builds on opt-in with `SE_DEV_GRAPHIFY=1` (the slow single-core fallback adds ~10-30 minutes; prepare reports this). `SE_DEV_GRAPHIFY=0` disables it entirely. Also covers the health check that detects an unusable (unclustered) graph and the clean-and-rebuild flow.
- **[GraphifyUsage.md](GraphifyUsage.md)** — how to query an existing graph (`query`/`explain`/`path`/`affected`), the large-graph load cap, and the query test scripts.

These two docs are fetched **on demand**: skip them entirely unless the user specifically wants the Graphify graph, so the extra tooling never pollutes context during normal work.

### Reference skills (read/search the game internals)
- **[se-dev-game-code](../se-dev-game-code/SKILL.md)** — Search decompiled C# of game **client**: how it works inside and the exact code you call or patch. Recommended companion for client mod/plugin work.
- **se-dev-game-book** (private, if installed) — Handbook on how the game **client** works inside, by subsystem with a page per type. Read it before searching the code for questions about how the game does something or which types take part.
- **[se-dev-server-code](../se-dev-server-code/SKILL.md)** — Search decompiled C# of **dedicated server**: how it works inside and the exact code you call or patch. Companion for server-side mod/plugin work.
- **se-dev-server-book** (private, if installed) — Handbook on how the **dedicated server** works inside, with the server-only parts called out. Read it before searching the code for questions about how the server does something.

The `*-book` handbooks (`se-dev-game-book`, `se-dev-server-book`, `se-dev-torch-book`) are
**private/internal** and distributed separately, not part of this public repository. When installed,
read them before searching code for any question about how the game works; without them, the
`*-code` skills answer those questions too and are the only reference. The books are not
authoritative: the decompiled source wins when the two disagree.

## How to pick

- **Programmable Block script?** → `se-dev-script` + `se-dev-game-code` for API details (`se-dev-game-book` first, if installed).
- **Steam Workshop mod?** → `se-dev-mod` + `se-dev-game-code` / `se-dev-server-code` as needed (the matching `*-book` first, if installed).
- **Client plugin?** → `se-dev-plugin` + `se-dev-game-code` (`se-dev-game-book` first, if installed).
- **Server plugin (Magnetar)?** → `se-dev-plugin` + `se-dev-plugin-sdk` + `se-dev-server-code` (`se-dev-server-book` first, if installed).
- **PluginHub / MagnetarHub / QuasarHub review?** → `se-dev-plugin-review` + the applicable host/code reference.
- **Maintaining a Torch plugin?** → `se-dev-torch` + `se-dev-torch-book` (and `se-dev-server-code`).
- **Need to understand how the game does X?** → `*-book` first if installed, then `*-code` to confirm the specifics; `*-code` alone otherwise.

Most non-trivial tasks pair an **authoring** skill with a **reference** skill: write with one, look up game's
internals with the other.

## Plugin templates

- [se-client-plugin-template](https://github.com/CometWorks/client-plugin-template) — client-only plugin.
- [se-server-plugin-template](https://github.com/CometWorks/server-plugin-template) — client + Magnetar server plugin (`ClientPlugin`, `ServerPlugin`, `Shared`). For **Torch** plugin, base it on template's `last-torch-compatible` tag, not `main`.

## Generic wisdom

- Stop and alert if the free disk space drops below 10GB on any partition you work on.
- Avoid using long timeouts. Be conscious on the wall clock time spent on completing tasks.
- To avoid wasting time, use monitoring scripts to poll for progress frequently, for example every few seconds.
- Do not use inference for monitoring, only read the output and react when relevant events happen.
- Always collect all evidence (logs, core dump, traceback) immediately, since log rotation and core dump cleanup may erase them.
- Operating system temporary folders (like /tmp or %TEMP%) may not be preserved over reboots, do not store anything important there which you may want to retrieve later
- On Linux the /tmp folder may consume memory (tmpfs), therefore do not store large files there.
- Consult a Fable or Astra sub-agent if you need deep planning or facing a difficult question/issue.

## Remarks

- Original source of these skills: https://github.com/CometWorks/skills
