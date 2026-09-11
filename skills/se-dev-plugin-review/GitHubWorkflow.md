# GitHub Preview and Posting

Use the available GitHub integration; otherwise use authenticated `gh`. Reading a PR is allowed during review. Posting is a separate external mutation.

## Initial review

Capture and retain:

- Canonical PR URL and `owner/repo#number`.
- Current PR head SHA.
- Exact Markdown under **PR comment preview**, saved as `comment.preview.md` beside root `review.json`.

Show the preview before any post. Keep the human-only checklist outside the preview unless an item is useful to the author.

`confirm` authorizes one comment only when one PR and one preview are active in the conversation. Editing the preview cancels earlier confirmation state. Never treat general agreement, `looks good`, or a confirmation for another action as authorization.

## On `confirm`

Do not ask again. Immediately:

1. Run `python3 scripts/post_review.py <review.json> <comment.preview.md>`.
2. The script verifies the current PR head against `hub_head_sha`, posts the exact file as a normal PR comment, and avoids duplicating an identical comment from the authenticated user.
3. If it reports a stale head, do not post. Regenerate artifacts, review the new source delta, and issue a new preview requiring a new `confirm`.
4. Return the created or existing comment URL. Do not convert the comment into an approval, request-changes review, merge, or edit another comment.

Do not bypass `post_review.py` with an inferred target or shell-interpolated body. The script uses authenticated `gh` without interpolating Markdown into a shell command.

If authentication is missing, report the exact setup blocker. Do not weaken the confirmation or stale-head checks.
