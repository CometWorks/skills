# QuasarHub Flow

Use this flow only for PRs in `CometWorks/quasar-hub`. Quasar plugins are trusted UI/server-management extensions inside the Quasar process, not Pulsar or Magnetar game plugins.

## Deterministic preparation

Run:

```bash
python3 scripts/prepare_quasar_review.py <PR-URL>
```

Use `--output <directory>` only when the default `~/.se-dev/reviews/CometWorks-quasar-hub-pr-<number>` location is unsuitable. The script rejects other hubs, fetches and parses exact base/head manifests, resolves `<RepoId>` and old/new `<Commit>` pins, and checks out pinned target source. A first registration or changed `<RepoId>` gets the complete tracked repository inventory in `source-tree.txt`; only a real `<Commit>` bump gets the direct `old_source_sha..new_source_sha` programmatic diff. Require `source.audit_scope` to match `review_type` before review.

It also requires `<PluginKind>QuasarUiPlugin</PluginKind>`, `<ProjectPath>`, and `<PackageManifest>` before source review. Inspect optional `<QuasarVersion>`, `<CompanionPluginIds>`, `<DependencyIds>`, `<Platforms>`, `<Recommended>`, and `<ImplicitLoading>` manually.

## Quasar-specific review

Follow [ReviewPaths.md](ReviewPaths.md) and [ReviewPolicy.md](ReviewPolicy.md), replacing game-plugin assumptions with Quasar's actual trust boundary:

- Treat `<ProjectPath>` and `<PackageManifest>` as roots of the executable/build closure.
- Inspect Razor/Blazor components, endpoints, authentication/authorization, JS interop, raw HTML/XSS boundaries, static assets, and `quasar-plugin.json`.
- Trace secrets, outbound requests, filesystem access, server-management actions, and companion Magnetar messages.
- Check UI assets/routes are scoped to the plugin and do not clobber Quasar or other plugins.
- Verify ordinary UI follows Quasar/MudBlazor conventions unless deviation is justified.
- Scrutinize `ImplicitLoading`; it expands installation impact but never authorizes plugin self-update code.

Use Quasar source or documentation to confirm host behavior. Do not apply Pulsar/Magnetar loader mechanics or multiplayer-cheat conclusions where they do not fit; evaluate authorization and managed-server impact instead.
