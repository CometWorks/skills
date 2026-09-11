---
name: se-dev-plugin-review
description: Review a plugin PR in StarCpt/PluginHub, CometWorks/magnetar-hub, or CometWorks/quasar-hub. Deterministically derives the target repository and exact source commit range from the hub manifest, previews concise feedback, and posts it after confirmation.
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

Then read:

1. [Review paths](ReviewPaths.md) and follow the script-selected `new_registration` or `version_bump` path.
2. [Review policy](ReviewPolicy.md) for security, fairness, filesystem, compatibility, performance, and readability gates.
3. [GitHub workflow](GitHubWorkflow.md) for preview and confirmed posting.

Use other `se-dev-*` skills instead of guessing:

- Client behavior or game API semantics: `se-dev-game-code`, optionally `se-dev-game-book`.
- Dedicated-server behavior: `se-dev-server-code`, optionally `se-dev-server-book`.
- Existing Pulsar/Magnetar plugin patterns: `se-dev-plugin`.
- Magnetar PluginSdk behavior: `se-dev-plugin-sdk`.

Do not trust PR descriptions, generated summaries, scanners, or another agent as proof. Read every in-scope change in context. Never report a check as passed unless it was actually performed.

## Caveman feedback

If `caveman-review` is available, load and apply it when drafting. Otherwise use the same discipline:

`path:Lline: <severity> <problem>. <concrete fix>.`

- `🔴 bug/security:` exploitable, destructive, cheaty, or broken behavior.
- `🟡 risk:` fragile behavior, compatibility damage, or likely noticeable performance cost.
- `🔵 nit:` optional cleanup only; omit low-value style comments.
- `❓ q:` a real decision-blocking question, not a disguised suggestion.

One actionable finding per line. Keep exact symbols and commit-pinned line links. Security findings may use one short paragraph when compression would hide the threat or evidence.

## Required result

Return three clearly separated blocks:

1. **Manual review required** — a short, scope-specific checklist of exact files/lines and behavior a human must personally verify. Highlight security-sensitive flow, packages/native files, and multiplayer-fairness judgment; say when a category is absent. New registrations get a broader checklist than version bumps. Never imply human sign-off happened.
2. **PR comment preview** — exact Markdown proposed for GitHub. Findings first, then only checks actually performed. If no actionable finding exists, say `No agent-detected blockers.` Never say `approved`, `safe`, `secure`, or `LGTM` on agent authority. End with `Human manual security review and approval still required.` Save this exact body as `comment.preview.md` beside root `review.json`.
3. **Post control** — exact hub PR, hub head SHA, target repository, and reviewed source SHA/range from `review.json`. Say `Reply confirm to post this exact comment.`

Do not post initially. When the user replies `confirm` for that PR, follow [GitHubWorkflow.md](GitHubWorkflow.md) immediately without asking again.
