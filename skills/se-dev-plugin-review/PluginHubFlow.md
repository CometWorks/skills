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
7. Writes `source.diff` from direct `old-source-SHA..new-source-SHA` comparison for a bump, or `source-tree.txt` for a new registration.
8. Records package, build, binary, native-file, and submodule inventory in `review.json`.

Read the generated root and per-plugin `review.json` files before reviewing. Do not substitute the target repository's default branch or hub PR SHAs for manifest pins.

## Registry checks

Read [the existing registry mechanics](../se-dev-plugin/Review.md) completely. Run the validator from the hub PR head and inspect source selection, assets, dependencies, alternate versions, runtime, and platform fields.

The hub manifest is authoritative. Do not report a target repository's backup manifest `<Commit>` as stale.

Then follow [ReviewPaths.md](ReviewPaths.md) and [ReviewPolicy.md](ReviewPolicy.md).
