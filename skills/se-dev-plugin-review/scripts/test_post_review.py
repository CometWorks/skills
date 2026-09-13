#!/usr/bin/env python3

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from _review_common import ReviewError
from post_review import post_review


class PostReviewTests(unittest.TestCase):
    def files(self) -> tuple[tempfile.TemporaryDirectory, Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        review = root / "review.json"
        body = root / "comment.preview.md"
        review.write_text(json.dumps({
            "schema_version": 1,
            "pr_url": "https://github.com/StarCpt/PluginHub/pull/1",
            "hub_repo": "StarCpt/PluginHub",
            "pr_number": 1,
            "hub_head_sha": "a" * 40,
        }), encoding="utf-8")
        body.write_text("Exact preview\n", encoding="utf-8")
        return temporary, review, body

    def test_rejects_stale_head(self):
        temporary, review, body = self.files()
        self.addCleanup(temporary.cleanup)
        stale_pr = {
            "head": {"sha": "b" * 40},
            "state": "open",
            "html_url": "https://github.com/StarCpt/PluginHub/pull/1",
        }
        with patch("post_review.gh_json", return_value=stale_pr):
            with self.assertRaises(ReviewError):
                post_review(review, body)

    def test_rejects_human_only_verification_material(self):
        temporary, review, body = self.files()
        self.addCleanup(temporary.cleanup)
        body.write_text(
            "Review body\n\n## Verification gaps\n\nManual test pending.\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ReviewError, "human-only verification material"):
            post_review(review, body)

        body.write_text(
            "Review body\n\nHuman manual security review and approval still required.\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ReviewError, "human-only verification material"):
            post_review(review, body)

    def test_identical_own_comment_is_not_duplicated(self):
        temporary, review, body = self.files()
        self.addCleanup(temporary.cleanup)

        def api(endpoint):
            if endpoint == "user":
                return {"login": "reviewer"}
            return {
                "head": {"sha": "a" * 40},
                "state": "open",
                "html_url": "https://github.com/StarCpt/PluginHub/pull/1",
            }

        comments = [{
            "user": {"login": "reviewer"},
            "body": "Exact preview\n",
            "html_url": "https://github.com/StarCpt/PluginHub/pull/1#issuecomment-1",
        }]
        with patch("post_review.gh_json", side_effect=api), patch("post_review.get_comments", return_value=comments):
            result = post_review(review, body)
        self.assertEqual(result, "Already posted: https://github.com/StarCpt/PluginHub/pull/1#issuecomment-1")


if __name__ == "__main__":
    unittest.main()
