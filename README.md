# Space Engineers Developer Skills

A [skill](https://agentskills.io) library for Space Engineers plugin, mod, and in-game script development.

**This library applies only to version 1 of the game.**

## How to use

You must have a "skills" compatible agentic coding environment. 
See [agentskills.io](https://agentskills.io) or [skills.sh](https://skills.sh) for details.

**After installing the skills make sure they work and the agent can actually access the files.**

In case of permission issues you have to grant access to the folder where the skills are stored. 
This usually happens if the skills are linked (`mklink`) into the coding agent's skills folder.

## Installation

`npx skills add viktor-ferenczi/se-dev-skills`

Follow the wizard.

Later you can update them by: `npx skills update`

In case you don't want to use `skills.sh`, then please see the "Manual installation" section below. 

## Preparation

The skills will automatically prepare themselves on **first use**. It means downloading some tools and indexing code.
If you want to prepare them ahead of time, simply run `Prepare.bat` in their respective folders.

**Note:** Preparing the `se-dev-game-code` skill may take 5–15 minutes, as it fully decompiles the game and builds
code indexes to allow for rapid code search later. The fully prepared repository takes about **1.5 GB** of disk space
due to the code index. If you need to save space, you can delete all `*.il` files (approx. **660 MB**), which are
only required for working on transpiler or preloader patches.

All skills install BusyBox (`busybox.exe`) into their folder for use by agentic coding tools for UNIX like commands,
because AI models are bad at Windows commands and often fall back to the UNIX CLI tools even if told otherwise. It
has improved efficiency a lot, therefore this is currently a requirement. 

If you want to use BusyBox in your other projects, then this is also available as a separate skill:
`npx skills add https://github.com/viktor-ferenczi/skills --skill busybox-on-windows`

## Skills

* [se-dev-script](skills/se-dev-script/SKILL.md) – In-game script development
* [se-dev-mod](skills/se-dev-mod/SKILL.md) – Mod development
* [se-dev-plugin](skills/se-dev-plugin/SKILL.md) – Plugin development
* [se-dev-game-code](skills/se-dev-game-code/SKILL.md) – Searchable decompiled C# game code (recommended companion for all the other skills)
* [se-dev-server-code](skills/se-dev-server-code/SKILL.md) – Searchable decompiled C# Dedicated Server code (for server side mod and plugin development)

_Enjoy!_

## Want to know more?

- [SE Mods Discord](https://discord.gg/PYPFPGf3Ca) FAQ, Troubleshooting, Support, Bug Reports, Discussion
- [Pulsar Discord](https://discord.gg/z8ZczP2YZY) Everything about plugins

---

## Manual installation

You can also install the skills manually:

1. Clone this repository
2. Run one of the installation scripts from the `install` folder:

| Target Environment | Script                              |
|--------------------|-------------------------------------|
| Claude Code        | `claude.bat`                        |
| Kilo Code          | `kilocode.bat`                      |
| Cline              | `cline.bat`                         |
| OpenCode           | `opencode.bat`                      |
| Custom location    | `install.bat <target_skills_folder>` |

The scripts create junction points (symlinks) from the target skill folders to the skill folders in this repository.

## FAQ

### How well does this work for plugin development?

I am currently testing it myself. It looks promising, but there may be rough edges. Please try it out and report back or
submit a PR!

### Why do the mod development skills lack details about non-scripting parts?

I haven't developed many mods involving custom art or definitions, so I lack the personal experience to add those yet.
Contributions via PR are very welcome.

### Does Claude Code know about the mod and script API whitelists?

I have exported the current whitelists (as of game version 1.208.015) using [MDK2](https://github.com/malforge/mdk2).
This may need future updates or automation during the preparation phase.

If you use the suggested mod or script template projects and the **ScriptMerge** tool, there is no formal whitelist
validation during build time. It may fail when loading into the game, but if you provide the relevant game logs to
Claude Code, it can usually identify and fix the issue.

### How does Claude Code load this much information into the context?

It doesn't! Skills work on the principle of **progressive disclosure**. Claude Code initially sees only the top-level
skill names and descriptions. It then gradually "discovers" more information as needed for the task. It has been given
specific instructions on how to search the SE codebase efficiently so it doesn't get overwhelmed.

Ideally, it performs research using sub-agents and clears irrelevant data before passing the results back to the parent
agent. Agent hierarchies are a fascinating and fast-evolving topic, definitely worth looking into!

### How much of this was "vibe-coded"?

The code indexing and search scripts were written entirely by Claude Code with zero human intervention, other than 
repeated prompting and some extra testing and review. The indexing logic is based on my previous work using 
Tree-sitter's C# parser, originally developed for the (now defunct) *Ask Your Code* ChatGPT plugin and GPT.

## Troubleshooting

If you suspect something is not working in these skills, then issue the following test prompt in an empty project:

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

In case of permission issues you have to grant access to the folder where the skills are stored. 
This usually happens if the skills are linked (`mklink`) into the coding agent's skills folder.

Example of a successful self-test result (generated by Claude Sonnet 4.5):

## Skills Verification Complete ✓

All four Space Engineers development skills are **visible, prepared, and working correctly**:

### Skills Status:
1. ✅ **se-dev-script** - Ready for PB (Programmable Block) script development
2. ✅ **se-dev-mod** - Ready for mod development
3. ✅ **se-dev-plugin** - Ready for plugin development
4. ✅ **se-dev-game-code** - Ready for game code exploration

### Smoke Test Results:

#### se-dev-game-code (Extensive Testing):
- ✅ **Class declaration search**: Found MyCubeGrid and related classes
- ✅ **Method declaration search**: Found GetCubeBlock in multiple locations
- ✅ **Field declaration search**: Found m_colorMaskHSV in MySlimBlock
- ✅ **Method usage search**: Found UpdateBeforeSimulation usage locations
- ✅ **Method signature search**: Displayed full method signatures with parameters
- ✅ **Hierarchy parent search**: Successfully found MyCubeGrid inherits from MyEntity
- ✅ **Hierarchy children search**: Successfully found MyEntity children with compressed namespace output
- ✅ **Content folder**: Accessible with game data (CubeBlocks, Blueprints, Localization, etc.)
- ✅ **Content data search**: Successfully found block definitions in .sbc files

#### se-dev-script:
- ✅ **PB API Whitelist**: Accessible and contains 600+ whitelisted types/members
- ✅ **Preparation**: Complete with Python virtual environment ready

#### se-dev-mod:
- ✅ **Mod API Whitelist**: Accessible and contains extensive mod API permissions
- ✅ **Preparation**: Complete with Python virtual environment ready

#### se-dev-plugin:
- ✅ **Documentation**: All guides accessible (Plugin.md, ClientPlugin.md, etc.)
- ✅ **Preparation**: Complete with Python virtual environment ready

### All Features Working:
- Code search with declarations and usages
- Class/interface hierarchy traversal
- Method signature inspection
- Field and property searching
- Content data exploration
- Namespace filtering and pagination
- Regex pattern matching
- Count and limit operations

**No issues found!** All skills are fully operational and ready for Space Engineers development tasks.

---

## Credits

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
