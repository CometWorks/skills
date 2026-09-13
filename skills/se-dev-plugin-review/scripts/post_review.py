#!/usr/bin/env python3
"""Post an exact review preview after verifying the hub PR head is unchanged."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _review_common import ReviewError, gh_json, run

SUPPORTED_HUBS = {"StarCpt/PluginHub", "CometWorks/magnetar-hub", "CometWorks/quasar-hub"}
FORBIDDEN_PR_BODY_MARKERS = (
    "## verification gaps",
    "human manual security review and approval still required.",
)


def get_comments(repo: str, number: int) -> list[dict[str, object]]:
    comments: list[dict[str, object]] = []
    page = 1
    while True:
        batch = gh_json(
            f"repos/{repo}/issues/{number}/comments",
            {"per_page": "100", "page": str(page)},
        )
        if not isinstance(batch, list):
            raise ReviewError("GitHub returned an invalid comment list")
        comments.extend(batch)
        if len(batch) < 100:
            return comments
        page += 1


def post_review(review_json: Path, body_file: Path) -> str:
    review = json.loads(review_json.read_text(encoding="utf-8"))
    body = body_file.read_text(encoding="utf-8")
    if not body.strip():
        raise ReviewError("Comment preview is empty")
    normalized_body = body.casefold()
    for marker in FORBIDDEN_PR_BODY_MARKERS:
        if marker in normalized_body:
            raise ReviewError(
                "Comment preview contains human-only verification material; keep it outside the PR body"
            )

    repo = str(review["hub_repo"])
    number = int(review["pr_number"])
    reviewed_head = str(review["hub_head_sha"])
    if repo not in SUPPORTED_HUBS or number < 1:
        raise ReviewError("Review metadata does not identify a supported hub PR")
    if review.get("schema_version") != 1:
        raise ReviewError("Unsupported review metadata schema")
    pr = gh_json(f"repos/{repo}/pulls/{number}")
    if not isinstance(pr, dict):
        raise ReviewError("GitHub returned invalid PR metadata")
    if pr.get("state") != "open":
        raise ReviewError(f"PR is {pr.get('state')}; refusing to post")
    if str(pr.get("html_url")) != str(review.get("pr_url")):
        raise ReviewError("Review metadata PR URL does not match GitHub")
    current_head = str(pr["head"]["sha"])
    if current_head != reviewed_head:
        raise ReviewError(
            f"Stale review: PR head changed from {reviewed_head} to {current_head}; regenerate the review"
        )

    viewer = gh_json("user")
    login = str(viewer["login"]) if isinstance(viewer, dict) else ""
    for comment in get_comments(repo, number):
        user = comment.get("user") if isinstance(comment, dict) else None
        author = str(user.get("login", "")) if isinstance(user, dict) else ""
        if author.lower() == login.lower() and comment.get("body") == body:
            return f"Already posted: {comment['html_url']}"

    payload = json.dumps({"body": body})
    result = json.loads(
        run(
            ["gh", "api", "--method", "POST", f"repos/{repo}/issues/{number}/comments", "--input", "-"],
            input_text=payload,
        )
    )
    return f"Posted: {result['html_url']}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_json", type=Path, help="Generated root review.json")
    parser.add_argument("body_file", type=Path, help="Exact displayed PR comment preview")
    args = parser.parse_args()

    try:
        print(post_review(args.review_json, args.body_file))
        return 0
    except (KeyError, OSError, ValueError, ReviewError) as error:
        print(f"error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
