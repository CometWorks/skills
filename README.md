# Space Engineers Developer Skills

[skill](https://agentskills.io) library for Space Engineers plugin, mod, in-game script development.

**This library applies only to version 1 of the game.**

## How to use

Need "skills" compatible agentic coding environment. 
See [agentskills.io](https://agentskills.io) or [skills.sh](https://skills.sh) for details.

**After installing skills, verify they work and agent can access files.**

Permission issues: grant access to folder where skills stored. 
Happens if skills linked (`mklink`) into coding agent's skills folder.

## Installation

`npx skills add CometWorks/skills`

Follow wizard.

Later update them by: `npx skills update`

Don't want to use `skills.sh`? See "Manual installation" section below. 

## Preparation

Skills auto-prepare on **first use**. Means downloading some tools and indexing code.
To prepare ahead of time, run `Prepare.bat` on Windows or `prepare.sh`
on Linux in respective skill folder. If any dependency missing, you
get failure message, so run preparation script from terminal where you can
see its output.

**Note:** Preparing `se-dev-game-code` skill may take 5–15 minutes, as it fully decompiles game and builds
code indexes for rapid code search later. Fully prepared repository takes about **1.5 GB** disk space
due to code index. To save space, delete all `*.il` files (approx. **660 MB**), only
required for working on transpiler or preloader patches.

On Windows skills install BusyBox (`busybox.exe`) into their folder for use by
agentic coding tools for UNIX like commands, because AI models are bad at Windows
commands and often fall back to UNIX CLI tools even if told otherwise. Improved
efficiency a lot, so currently a requirement there.

On Linux skills use native shell tools instead. Decompiler skills
(`se-dev-game-code`, `se-dev-server-code`) install `ilspycmd` with official ILSpy
dotnet tool frontend, so PowerShell not required to prepare and run skills.

To use BusyBox in your other projects, also available as separate skill:
`npx skills add https://github.com/viktor-ferenczi/skills --skill busybox-on-windows`

## Skills

* [se-dev](skills/se-dev/SKILL.md) – Big-picture overview and table of contents for all skills below (start here)
* [se-dev-script](skills/se-dev-script/SKILL.md) – In-game script development
* [se-dev-mod](skills/se-dev-mod/SKILL.md) – Mod development
* [se-dev-plugin](skills/se-dev-plugin/SKILL.md) – Plugin development (client via Pulsar, server via Magnetar)
* [se-dev-game-code](skills/se-dev-game-code/SKILL.md) – Searchable decompiled C# game code (recommended companion for all other skills)
* [se-dev-server-code](skills/se-dev-server-code/SKILL.md) – Searchable decompiled C# Dedicated Server code (for server side mod and plugin development)
* [se-dev-torch](skills/se-dev-torch/SKILL.md) – Torch plugin development and Torch source search (legacy; Torch-only)

_Enjoy!_

## Want to know more?

- [SE Mods Discord](https://discord.gg/PYPFPGf3Ca) FAQ, Troubleshooting, Support, Bug Reports, Discussion
- [Pulsar Discord](https://discord.gg/z8ZczP2YZY) Everything about plugins

---

## Manual installation

Install skills manually:

1. Clone this repository
2. Run one of installation scripts from `install` folder:

| Target Environment | Windows Script                      | Linux Script                  |
|--------------------|-------------------------------------|-------------------------------------|
| Claude Code        | `claude.bat`                        | `claude.sh`                         |
| Kilo Code          | `kilocode.bat`                      | `kilocode.sh`                       |
| Cline              | `cline.bat`                         | `cline.sh`                          |
| OpenCode           | `opencode.bat`                      | `opencode.sh`                       |
| Custom location    | `install.bat <target_skills_folder>` | `install.sh <target_skills_folder>` |

Scripts create junction points / symlinks from target skill folders to skill folders in this repository.

They install all skills listed in [Skills](#skills) section above.

## FAQ

### How well does this work for plugin development?

Currently testing it myself. Looks promising, but may have rough edges. Try it out and report back or
submit a PR!

### Why do the mod development skills lack details about non-scripting parts?

Haven't developed many mods involving custom art or definitions, so lack personal experience to add those yet.
Contributions via PR welcome.

### Does Claude Code know about the mod and script API whitelists?

Exported current whitelists (as of game version 1.208.015) using [MDK2](https://github.com/malforge/mdk2).
May need future updates or automation during preparation phase.

If you use suggested mod or script template projects and **ScriptMerge** tool, no formal whitelist
validation during build time. May fail when loading into game, but if you provide relevant game logs to
Claude Code, it can usually identify and fix the issue.

### How does Claude Code load this much information into the context?

It doesn't! Skills work on principle of **progressive disclosure**. Claude Code initially sees only top-level
skill names and descriptions. Then gradually "discovers" more information as needed for the task. Given
specific instructions on how to search SE codebase efficiently so it doesn't get overwhelmed.

Ideally, performs research using sub-agents and clears irrelevant data before passing results back to parent
agent. Agent hierarchies are fascinating and fast-evolving topic, worth looking into!

### How much of this was "vibe-coded"?

Code indexing and search scripts written entirely by Claude Code with zero human intervention, other than 
repeated prompting and some extra testing and review. Indexing logic based on my previous work using 
Tree-sitter's C# parser, originally developed for (now defunct) *Ask Your Code* ChatGPT plugin and GPT.

## Troubleshooting

If you suspect something not working in these skills, issue the following test prompt in empty project:

_Add `se-dev-server-code` to the list if you plan to develop server side plugins._

```md
Check whether you can see these skills:
- `se-dev-script`
- `se-dev-mod`
- `se-dev-plugin`
- `se-dev-game-code`

If you see them, then make sure they're prepared for first use.

Once they are prepared, conduct some smoke testing on their features to make sure they work.

If something is missing or not working properly, then list those in a final summary.
```

Permission issues: grant access to folder where skills stored. 
Happens if skills linked (`mklink`) into coding agent's skills folder.

## Credits

### Developers

- OwendB

### Patreon Supporters

_in alphabetical order_

#### Admiral level

- BetaMark
- Casinost
- Mordith - Guardians SE
- Robot10
- wafoxxx

#### Captain level

- Diggz
- jiringgot
- Jimbo
- Kam Solastor
- lazul
- Linux123123
- Lotan
- Lurking StarCpt
- NeonDrip
- NeVaR
- opesoorry

#### Testers

- Avaness
- mkaito

### Creators

- Space - Pulsar
- avaness - Plugin Loader (legacy)
- Fred XVI - Racing maps
- Kamikaze - M&M mod
- LTP
- Mordith - Guardians SE
- Mike Dude - Guardians SE
- SwiftyTech - Stargate Dimensions

**Thank you very much for all your support!**

### Legal

Space Engineers is trademark of Keen Software House s.r.o.
