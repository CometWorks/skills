#!/usr/bin/env python3

import unittest

from _review_common import ReviewError, classify, parse_manifest, parse_pr_url, validate_manifest


class PrepareReviewTests(unittest.TestCase):
    def test_supported_pr(self):
        self.assertEqual(
            parse_pr_url(
                "https://github.com/StarCpt/PluginHub/pull/187",
                {"StarCpt/PluginHub", "CometWorks/magnetar-hub"},
            ),
            ("StarCpt/PluginHub", 187),
        )

    def test_rejects_lookalike_hub(self):
        with self.assertRaises(ReviewError):
            parse_pr_url(
                "https://github.com/example/PluginHub/pull/187",
                {"StarCpt/PluginHub", "CometWorks/magnetar-hub"},
            )

    def test_game_flow_rejects_quasar_hub(self):
        with self.assertRaises(ReviewError):
            parse_pr_url(
                "https://github.com/CometWorks/quasar-hub/pull/1",
                {"StarCpt/PluginHub", "CometWorks/magnetar-hub"},
            )

    def test_manifest_fields(self):
        manifest = parse_manifest(
            b"""<PluginData><Id>x</Id><RepoId>owner/repo</RepoId><Commit>abc1234</Commit>
            <SourceDirectories><Directory>ClientPlugin</Directory></SourceDirectories>
            <NuGetReferences><PackageReference Include="X" Version="1" /></NuGetReferences>
            </PluginData>""",
            "test",
        )
        self.assertEqual(manifest["repo_id"], "owner/repo")
        self.assertEqual(manifest["commit"], "abc1234")
        self.assertEqual(manifest["source_directories"], ["ClientPlugin"])

    def test_quasar_requires_quasar_fields(self):
        manifest = parse_manifest(
            b"<PluginData><RepoId>owner/repo</RepoId><Commit>abc1234</Commit></PluginData>",
            "test",
        )
        with self.assertRaises(ReviewError):
            validate_manifest(manifest, "quasar", "Plugins/Test.xml")
        validate_manifest(manifest, "pulsar_magnetar", "Plugins/Test.xml")

    def test_classifies_supply_chain_files(self):
        result = classify(["Directory.Packages.props", "native/a.so", "lib/X.dll", "src/A.csproj"])
        self.assertEqual(result["package_files"], ["Directory.Packages.props"])
        self.assertEqual(result["native_files"], ["native/a.so"])
        self.assertEqual(result["binary_files"], ["lib/X.dll"])
        self.assertEqual(result["build_files"], ["Directory.Packages.props", "src/A.csproj"])


if __name__ == "__main__":
    unittest.main()
