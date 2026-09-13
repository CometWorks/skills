---
name: se-dev-plugin-review
description: Review a plugin PR in StarCpt/PluginHub, CometWorks/magnetar-hub, or CometWorks/quasar-hub. Deterministically derives the target repository and exact source commit range from the hub manifest, produces an evidence-backed review preview, and posts it after confirmation.
license: MIT
---

# Space Engineers Plugin Review

One supported hub PR URL is the complete input. Do not ask the user for the target repository or commit range; derive them from the changed registry manifest with the supplied script.

The preparation and posting scripts require Python 3.11+, Git, and authenticated GitHub CLI (`gh`). If any is unavailable, report that concrete setup blocker instead of reconstructing review metadata by inference.

Example:

`Use se-dev-plugin-review on https://github.com/StarCpt/PluginHub/pull/123`

## Route by hub

- `StarCpt/PluginHub` or `CometWorks/magnetar-hub`: read [PluginHub and MagnetarHub flow](PluginHubFlow.md), then run `scripts/prepare_plugin_review.py <PR-URL>`.
- `CometWorks/quasar-hub`: read [QuasarHub flow](QuasarHubFlow.md), then run `scripts/prepare_quasar_review.py <PR-URL>`.
- Reject lookalike or unsupported repositories.

Both scripts save exact hub metadata, base/head manifests, resolved source SHAs, a pinned source checkout, and either a direct version diff or full-tree inventory under `~/.se-dev/reviews/` by default. Treat `review.json` as authoritative routing data; do not infer or rewrite its repository, review type, or SHA range.

This routing is a hard gate. `new_registration` (including a changed target repository) requires an audit of every tracked path at the pinned source SHA and must not use a diff. Only `version_bump`, as derived from the hub PR's base/head manifests, may use the programmatic direct-commit diff. Stop on a mismatched `source.audit_scope` instead of narrowing or inventing review scope.

Then read:

1. [Review paths](ReviewPaths.md) and follow the script-selected `new_registration` or `version_bump` path.
2. [Review policy](ReviewPolicy.md) for security, fairness, filesystem, compatibility, performance, and readability gates.
3. [Review style and evidence provenance](ReviewStyle.md) for the GitHub review body.
4. [GitHub workflow](GitHubWorkflow.md) for preview and confirmed posting.

Use other `se-dev-*` skills instead of guessing:

- Client behavior or game API semantics: `se-dev-game-code`, optionally `se-dev-game-book`.
- Dedicated-server behavior: `se-dev-server-code`, optionally `se-dev-server-book`.
- Existing Pulsar/Magnetar plugin patterns: `se-dev-plugin`.
- Magnetar PluginSdk behavior: `se-dev-plugin-sdk`.

Do not trust PR descriptions, generated summaries, scanners, or another agent as proof. Read every in-scope change in context. Never report a check as passed unless it was actually performed.

## Finding discipline

Keep exact symbols and commit-pinned line links. Findings must expose the causal chain, impact, evidence, fix, and relevant tradeoff. Omit taste-only feedback. If `caveman-review` is active, it applies to conversational summaries only; the saved GitHub review body follows [ReviewStyle.md](ReviewStyle.md).

## Required result

Return three clearly separated blocks:

1. **Manual review required** — a short, scope-specific checklist of exact files/lines and behavior a human must personally verify. Highlight security-sensitive flow, packages/native files, and multiplayer-fairness judgment; say when a category is absent. New registrations get a broader checklist than version bumps. Never imply human sign-off happened.
2. **PR comment preview** — exact Markdown proposed for GitHub, structured per [ReviewStyle.md](ReviewStyle.md). If no actionable finding exists, say `No agent-detected blockers.` Never say `approved`, `safe`, `secure`, or `LGTM` on agent authority. Do not include a `Verification gaps` section, the human-only checklist, blanket runtime-test limitations, or human-manual-review/approval boilerplate; keep those in the conversational **Manual review required** block. Save the exact PR body as `comment.preview.md` beside root `review.json`.
3. **Post control** — exact hub PR, hub head SHA, target repository, and reviewed source SHA/range from `review.json`. Say `Reply confirm to post this exact comment.`

Do not post initially. When the user replies `confirm` for that PR, follow [GitHubWorkflow.md](GitHubWorkflow.md) immediately without asking again.

For a new registration, the performed-checks summary must also state the complete repository path count and name any unaccounted path; an unaccounted path means the full-repository gate did not pass. In every path, state project/MSBuild reference status separately from hub-manifest packages and committed binary/native-file status. Name unresolved provenance or unevaluated imports explicitly.
