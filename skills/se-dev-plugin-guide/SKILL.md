---
name: se-dev-plugin-guide
description: Developer guide for Space Engineers 1 plugins - which template to pick (client, client+server, Quasar), where to learn the game's internals, patching basics, testing locally with Pulsar/Magnetar, how players' PCs differ, filling the hub manifest XML, submitting to PluginHub/MagnetarHub/QuasarHub, and developing with AI coding agents. Use it to answer a plugin developer's process questions or to take a plugin from template to hub release.
license: MIT
allowed-tools: Read
---

# SE1 Plugin Developer Guide

**Applies only to Space Engineers version 1.** For SE2 use the `se2-dev-plugin-guide` skill from
[CometWorks/skills2](https://github.com/CometWorks/skills2).

The workflow around a plugin: start, test, publish, maintain. Written for human developers; agents use it to
answer their questions or to do the steps for them. The same text is on the web at
https://cometworks.github.io/plugin-dev/se1/. Writing the plugin's code is the job of
[`se-dev-plugin`](../se-dev-plugin/SKILL.md) (patching handbook, search in other plugins) and
[`se-dev-game-code`](../se-dev-game-code/SKILL.md) (the game's code).

## Topics

Read only the page the question needs:

| Question | Page |
|---|---|
| Which template, how to start a project | [Templates.md](Templates.md) |
| Where to learn how the game works inside | [GameInternals.md](GameInternals.md) |
| Harmony, transpilers, preloader, publicizer: the basics | [PatchingBasics.md](PatchingBasics.md) |
| Pulsar paths and options, dev folders, DLL deploy, profiles, debugging, Magnetar, Linux | [LocalTesting.md](LocalTesting.md) |
| Why it works locally but fails for players | [LocalVsPlayers.md](LocalVsPlayers.md) |
| The hub manifest XML, field by field | [Manifest.md](Manifest.md) |
| Submitting to PluginHub, MagnetarHub, QuasarHub; updates; registering a Workshop mod | [Submitting.md](Submitting.md) |
| Using coding agents and these skills | [AiAgents.md](AiAgents.md) |
| C# version, NuGet, data files, Linux | [FAQ.md](FAQ.md) |

## Key facts

- Client plugins: [client-plugin-template](https://github.com/CometWorks/client-plugin-template), loaded by
  [Pulsar](https://github.com/SpaceGT/Pulsar), listed on [PluginHub](https://github.com/StarCpt/PluginHub).
- Client + server or server-only: [server-plugin-template](https://github.com/CometWorks/server-plugin-template),
  server part loaded by [Magnetar](https://github.com/CometWorks/magnetar), listed on
  [MagnetarHub](https://github.com/CometWorks/magnetar-hub).
- Players' PCs compile the plugin from its GitHub source at the manifest's `Commit`, with Roslyn and no
  MSBuild. Test the Release build through a Pulsar development folder before every release.
- Never publish decompiled game or server code.
- Questions the guide doesn't answer: the [Pulsar Discord](https://discord.gg/z8ZczP2YZY).

## Remarks

Original source of this skill: https://github.com/CometWorks/skills
