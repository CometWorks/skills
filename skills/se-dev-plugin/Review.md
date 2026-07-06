# Reviewing Plugins for PluginHub / MagnetarHub

How to review a submission (or update) to a plugin registry before it is merged:

- **PluginHub** — client plugins, loaded by [Pulsar](https://github.com/SpaceGT/Pulsar). Registry: [StarCpt/PluginHub](https://github.com/StarCpt/PluginHub/).
- **MagnetarHub** — server plugins, loaded by [Magnetar](https://magnetar.se). Registry: [CometWorks/magnetar-hub](https://github.com/CometWorks/magnetar-hub).

Both registries use the **same** GitHub-plugin XML schema and the **same** validator (`test.py`). A submission is a PR that adds/updates a single `Plugins/<Name>.xml` pointing at a GitHub repo + commit. Review is a **best-effort** safety/security gate — there is no legal guarantee — so be thorough and, when in doubt, ask the author rather than merge.

## Trust model (why this matters)

Plugins run as **native, unsandboxed .NET code with full trust** — they can do anything the user (client) or the server process can. There is no permission system. The only protection is that:

1. All plugins **must be open source**, and
2. The registry pins an exact **GitHub repo + commit**; Pulsar/Magnetar **compile from that source on the end machine** (Roslyn), so what ships is exactly what you can read at that commit.

Your review therefore covers **both the manifest and the source at the pinned commit**. If you review commit A and the author later bumps the pin to B, you must re-review the delta.

## Step 1 — Manifest conformance (mechanical gate)

Run the registry's own validator, then eyeball the file:

```bash
python3 test.py Plugins        # from the registry repo root; must print "All files validated"
```

The validator requires (identical for both hubs):
- File lives under `Plugins/` (mods under `Plugins/Mods/`).
- Root element `xsi:type="GitHubPlugin"` (or `ModPlugin` for a mod).
- Non-empty `<Id>`, `<FriendlyName>`, `<Author>`.
- `<Commit>` present and matching `^[0-9a-f]+$`.

Conventions and optional fields:
- **Id**: PluginHub uses `Owner/Repo`; MagnetarHub uses a **GUID** with the repo in `<RepoId>`.
- `<SourceDirectories><Directory>…</Directory></SourceDirectories>` — only these compile; confirm test/sample projects are excluded. Omitted = whole repo compiles.
- `<NuGetReferences>` — third-party deps restored at compile (see Step 3, committed binaries).
- `<AssetFolder>` — asset dir handed to `Plugin.LoadAssets(path)`.
- `<Runtimes>` (e.g. `NETFramework`), `<Hidden>` (dependency-only plugins), `<DependencyIds>`, `<AlternateVersions>`.

## Step 2 — Commit pin == reviewed code

```bash
git clone <repo> && cd <repo>
git rev-parse HEAD          # must equal <Commit> in the manifest
```

Do this at the start **and** after any pin bump in the PR conversation. A mismatch means you'd be approving code you haven't seen.

## Step 3 — Security review of the source (the real work)

Clone at the pinned commit and audit every `*.cs`. Grep for the patterns below, then verify each hit **in context** (don't flag on the keyword alone). Delegate the large files to a sub-agent and keep only the conclusions.

Red flags:

- **Dynamic code execution** — `Assembly.Load`/`LoadFrom`/`LoadFile` of bytes from disk, network, or a decoded blob; `Activator.CreateInstance` on types chosen by untrusted data; runtime `CSharpCodeProvider`/Roslyn compile; `Emit`/`DynamicMethod`/`ILGenerator`; reflection `Invoke` driven by remote input. (Loading a *bundled, embedded* library is acceptable — but prefer NuGet, see committed binaries.)
- **Decrypted / obfuscated code** — crypto (`Aes`/`Rijndael`/`XOR`/…) or `FromBase64String`/`GZip`/`Deflate` whose output is then `Assembly.Load`ed or eval'd. (DPAPI `ProtectedData` for a locally-stored token, and base64 of GitHub blob content, are benign.)
- **Shell / process** — `Process.Start`, `ProcessStartInfo`, `cmd`/`powershell`/`bash`. Check the **exact argument**: opening a fixed `https://…` URL in the browser is fine; an attacker- or remote-controlled command/path is not.
- **Network / exfiltration** — enumerate **every** HTTP(S) host contacted. Anything beyond what the plugin legitimately needs (e.g. `api.github.com` for a GitHub-backed plugin, `steamcommunity.com` for Workshop) is a red flag: telemetry, analytics, webhooks, pastebin, IP loggers. Trace where **tokens, credentials, SteamID, machine info, local files** go — they must never leave except to their legitimate service.
- **Committed binaries** — plugins should reference deps via `<PackageReference>`/`<NuGetReferences>`, **not** commit prebuilt DLLs (a compiled binary defeats the open-source/compile-from-source guarantee). If a `*.dll` is committed, require replacement with a NuGet reference. If it must stay, verify each one **byte-for-byte** against the official package:

  ```bash
  curl -sSL -o pkg.nupkg "https://www.nuget.org/api/v2/package/<Id>/<Version>"
  unzip -j pkg.nupkg "lib/<tfm>/<Name>.dll" -d ext
  sha256sum committed/<Name>.dll ext/<Name>.dll   # must match exactly
  ```
- **Obfuscation** — char-array/hex/base64 string reconstruction that hides URLs or payloads.
- **Game-specific abuse** — e.g. capturing or reading grids the player doesn't own in multiplayer (must gate on the engine's own `HasAccess` / safe-zone checks, mirroring vanilla); leaking private data (a blueprint plugin should scrub owner / SteamID64 / GPS coordinates before upload). Client-side gates mirror vanilla and can't be server-enforced — note this as a known limitation, not a blocker.

## Step 4 — It must build from source under the loader

The registry compiles from source on the **end machine**, not from the author's IDE output — a plugin that builds in Visual Studio can still fail Pulsar's/Magnetar's from-source Roslyn compile. Verify it actually compiles that way:

- **Client**: dev-folder test under Pulsar / the Headless build — register the repo as a dev folder (`DebugBuild=true` = from-source), launch, and confirm it compiles (`Compiling files from …`) and its `Init` runs with **no CS#### errors and no exceptions**.
- **Publicizer**: if the plugin publicizes game assemblies, the source must supply the `IgnoresAccessChecksTo` attribute for the from-source path (Krafs.Publicizer only injects it in the MSBuild build, which the registry does not use). See [Publicizer.md](Publicizer.md).
- Confirm `<NuGetReferences>` and `<SourceDirectories>` in the manifest match what the source actually needs.

## Step 5 — Process / conversation

- Read the PR thread: confirm the author addressed prior review comments and **bumped the pin** to include the fixes.
- Surface residual items even when non-blocking (e.g. a stale in-repo manifest commit, docs describing removed behavior).
- Merge only when the mechanical gate, the security review, and the from-source build/load all pass — or defer with specific asks.

## Quick checklist

- [ ] `test.py` passes; manifest fields + Id/RepoId convention correct
- [ ] `<Commit>` == reviewed `git rev-parse HEAD` (re-check after pin bumps)
- [ ] No dynamic / decrypted / obfuscated code execution
- [ ] No unexpected network hosts; no token/credential/machine-info exfiltration
- [ ] `Process.Start` arguments are fixed/safe
- [ ] No committed binaries (or every one byte-verified against official NuGet)
- [ ] Compiles from source under the loader; `Init` loads with no errors
- [ ] Game-specific abuse gated (ownership/safe-zone; privacy scrub)
- [ ] Prior review comments addressed and pin bumped
