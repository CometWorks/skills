# Develop with AI coding agents

Coding agents such as Claude Code work well on plugins when they have the right context.

- **Install the skills.** `npx skills add CometWorks/skills` installs the
  [Space Engineers developer skills](https://github.com/CometWorks/skills): `se-dev` (start here),
  `se-dev-plugin` (patching handbook, search in other plugins' code), `se-dev-game-code` and
  `se-dev-server-code` (decompiled code search), `se-dev-plugin-review` (hub review) and
  `se-dev-plugin-guide` (this guide). Prepare them once, or let the agent do it on first use.
- **Use the template's `AGENTS.md`.** It points the agent to the skills; humans can read it too.
- **Let the agent build.** The SDK-style projects build with `dotnet build`, so the agent can build, read
  the errors and fix them in a loop without you. Ask it to read the game code it patches before it writes
  the patch.
- **Give it the evidence.** Paste or point it at Pulsar's `info.log` and the game log when something
  fails; it can usually find the cause.
- **Test in the game yourself.** The agent can't see the game. Do the Release test from
  [Test your plugin locally](LocalTesting.md) before every release.
- **Review before you submit.** Ask the agent to check your code against the review policy of the
  `se-dev-plugin-review` skill ([ReviewPolicy.md](../se-dev-plugin-review/ReviewPolicy.md)), the one hub reviewers use, before you open the hub pull request.
- **Keep game updates cheap.** After an update, ask the agent to compare the old and new game code of the
  methods you patch.
- **Don't publish decompiled code**, not even in an issue or a pull request.

Agents cost money if you use them a lot, but they save a lot of time on this kind of work.

## When you are the agent

- Start from [`se-dev`](../se-dev/SKILL.md) for the skill map, then read the project's `AGENTS.md` and
  `README.md`.
- Read the game code you patch before you write the patch ([`se-dev-game-code`](../se-dev-game-code/SKILL.md),
  [`se-dev-server-code`](../se-dev-server-code/SKILL.md) for server plugins).
- Build with `dotnet build` and fix every error and warning you introduced. A green build is not the release
  check: Pulsar compiles differently ([LocalVsPlayers.md](LocalVsPlayers.md)).
- Keep the manifest in step with the code: new source folders go into `SourceDirectories`, every NuGet package
  in the `.csproj` also goes into `NuGetReferences`, data files become `Asset` entries ([Manifest.md](Manifest.md)).
- Code under `#if DEBUG` or `#if LOCAL_BUILD` doesn't exist in the players' build.
- You can't run the game. Ask the developer to do the in-game Release test ([LocalTesting.md](LocalTesting.md))
  and to give you Pulsar's `info.log` and the game log when something fails.
- Put the commit hash into the manifest only after that commit is pushed to the public repository.
- Never commit, paste or quote decompiled game code outside the developer's machine.
