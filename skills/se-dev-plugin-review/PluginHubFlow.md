# PluginHub and MagnetarHub Flow

Use this shared flow only for PRs in `StarCpt/PluginHub` or `CometWorks/magnetar-hub`.

## Deterministic preparation

Run:

```bash
python3 scripts/prepare_plugin_review.py <PR-URL>
```

Use `--output <directory>` only when the default `~/.se-dev/reviews/<hub>-pr-<number>` location is unsuitable. The script:

1. Validates the PR belongs to one of these two exact hubs.
2. Fetches PR base/head SHAs and changed `Plugins/*.xml` files through GitHub.
3. Parses complete base/head XML manifests.
4. Reads `<RepoId>` and authoritative old/new `<Commit>` pins.
5. Resolves pins to full target-repository SHAs.
6. Checks out the exact new source SHA.
7. Selects the audit gate from the manifest change in the hub PR. A first registration or changed `<RepoId>` writes `source-tree.txt` for the complete tracked repository at `new_source_sha`; only a real `<Commit>` bump writes `source.diff` from the direct `old-source-SHA..new-source-SHA` comparison.
8. Records package, build, binary, native-file, submodule, and static MSBuild-reference inventory in `review.json`.

Read the generated root and per-plugin `review.json` files before reviewing. Do not substitute the target repository's default branch or hub PR SHAs for manifest pins.
Require `source.audit_scope` to match `review_type`: `full_repository_tree` for `new_registration`, `direct_commit_diff` for `version_bump`. Stop if it does not. Never synthesize a new-registration diff against the target's parent, empty tree, default branch, or latest commit.
Treat `msbuild_references` as an audit index, not proof of the evaluated build graph: imports, conditions, SDK defaults, and generated files can add or remove references.

## Registry checks

Read [the existing registry mechanics](../se-dev-plugin/Review.md) completely. It is the baseline checklist; this skill's deterministic scope, full-repository, provenance, and multiplayer-authority rules take precedence where they are newer or stricter.

Run the validator from the hub PR head, then inspect the manifest yourself. Verify its location and plugin type (including `Plugins/Mods` and `ModPlugin` where applicable), required identity fields, current `Id`/`RepoId` convention, commit syntax, source selection, dependencies, alternate versions, runtime/platform restrictions, and hidden/dependency-only behavior against the hub's current schema. Do not hard-code a historical identity convention when the checked-out validator/schema says otherwise.

Trace loader semantics, not just XML presence:

- Omitted `SourceDirectories` means the whole repository is selected for compilation; when present, ensure required source is included and tests, samples, and tooling are excluded.
- `NuGetReferences` are restored for loader compilation; project-file package/reference declarations are not a substitute.
- `AssetFolder` is handed to the plugin asset-loading callback; audit that asset closure and path.
- Resolve `DependencyIds`, `AlternateVersions`, `Hidden`, runtime, and platform fields far enough to establish what is installed and loaded together.

The hub manifest is authoritative. Do not report a target repository's backup manifest `<Commit>` as stale. If a backup manifest exists, ignore its commit value but compare other loader-relevant fields such as source directories, NuGet references, assets, and dependencies for meaningful drift.

Then follow [ReviewPaths.md](ReviewPaths.md) and [ReviewPolicy.md](ReviewPolicy.md).
