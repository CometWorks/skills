#!/usr/bin/env python3

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from _review_common import (
    ReviewError,
    classify,
    inventory_msbuild_references,
    parse_manifest,
    parse_pr_url,
    prepare_source,
    validate_manifest,
)


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

    def test_inventories_msbuild_references(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / "src" / "Plugin.csproj"
            project.parent.mkdir()
            project.write_text(
                """<Project><ItemGroup>
                <Reference Include="DirectShowLib, Version=2.1.0.1599">
                  <HintPath>$(Bin64Dir)DirectShowLib.dll</HintPath><Private>False</Private>
                </Reference>
                <ProjectReference Include="../Shared/Shared.csproj" />
                <PackageReference Include="Lib.Harmony" Version="2.4.2" />
                </ItemGroup></Project>""",
                encoding="utf-8",
            )

            result = inventory_msbuild_references(root, ["src/Plugin.csproj", "README.md"])

            self.assertEqual(result["msbuild_reference_files"], ["src/Plugin.csproj"])
            self.assertEqual(result["msbuild_reference_parse_errors"], [])
            self.assertEqual(
                [(item["kind"], item["include"]) for item in result["msbuild_references"]],
                [
                    ("Reference", "DirectShowLib, Version=2.1.0.1599"),
                    ("ProjectReference", "../Shared/Shared.csproj"),
                    ("PackageReference", "Lib.Harmony"),
                ],
            )
            self.assertEqual(
                result["msbuild_references"][0]["hint_path"],
                "$(Bin64Dir)DirectShowLib.dll",
            )
            self.assertEqual(result["msbuild_references"][0]["private"], "False")

    def test_new_registration_scopes_entire_tree_without_diff(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            (source / ".git").mkdir(parents=True)
            (root / "source.diff").write_text("stale", encoding="utf-8")
            (root / "changed-files.txt").write_text("stale", encoding="utf-8")

            def fake_run(args, cwd=None, input_text=None):
                if args[:4] == ["git", "remote", "get-url", "origin"]:
                    return "https://github.com/owner/repo.git\n"
                if args[:4] == ["git", "ls-tree", "-r", "--full-tree"]:
                    return (
                        "100644 blob " + "1" * 40 + "\tREADME.md\n"
                        "100644 blob " + "2" * 40 + "\tsrc/Plugin.cs\n"
                    )
                return ""

            with patch("_review_common.run", side_effect=fake_run) as mocked_run:
                result = prepare_source(
                    root, "owner/repo", None, "a" * 40, "new_registration"
                )

            commands = [call.args[0] for call in mocked_run.call_args_list]
            self.assertFalse(any(command[:2] == ["git", "diff"] for command in commands))
            self.assertEqual(result["audit_scope"], "full_repository_tree")
            self.assertEqual(result["scope_artifact"], "source-tree.txt")
            self.assertEqual(result["repository_file_count"], 2)
            self.assertEqual(result["scope_file_count"], 2)
            self.assertEqual(
                (root / "source-tree.txt").read_text(encoding="utf-8"),
                "README.md\nsrc/Plugin.cs\n",
            )
            self.assertFalse((root / "source.diff").exists())
            self.assertFalse((root / "changed-files.txt").exists())

    def test_version_bump_uses_only_direct_commit_diff_scope(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            (source / ".git").mkdir(parents=True)
            (root / "source-tree.txt").write_text("stale", encoding="utf-8")
            old_sha = "b" * 40
            new_sha = "c" * 40

            def fake_run(args, cwd=None, input_text=None):
                if args[:4] == ["git", "remote", "get-url", "origin"]:
                    return "https://github.com/owner/repo.git\n"
                if args[:4] == ["git", "ls-tree", "-r", "--full-tree"]:
                    return (
                        "100644 blob " + "1" * 40 + "\tREADME.md\n"
                        "100644 blob " + "2" * 40 + "\tsrc/Plugin.cs\n"
                    )
                if args[:3] == ["git", "diff", "--binary"]:
                    return "diff --git a/src/Plugin.cs b/src/Plugin.cs\n"
                if args[:3] == ["git", "diff", "--name-status"]:
                    return "M\tsrc/Plugin.cs\n"
                return ""

            with patch("_review_common.run", side_effect=fake_run) as mocked_run:
                result = prepare_source(
                    root, "owner/repo", old_sha, new_sha, "version_bump"
                )

            commands = [call.args[0] for call in mocked_run.call_args_list]
            diff_commands = [command for command in commands if command[:2] == ["git", "diff"]]
            self.assertEqual(len(diff_commands), 2)
            self.assertTrue(all(f"{old_sha}..{new_sha}" in command for command in diff_commands))
            self.assertEqual(result["audit_scope"], "direct_commit_diff")
            self.assertEqual(result["scope_artifact"], "source.diff")
            self.assertEqual(result["repository_file_count"], 2)
            self.assertEqual(result["scope_file_count"], 1)
            self.assertFalse((root / "source-tree.txt").exists())

    def test_version_bump_requires_old_sha(self):
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ReviewError, "requires an old source SHA"):
                prepare_source(
                    Path(temp), "owner/repo", None, "d" * 40, "version_bump"
                )


if __name__ == "__main__":
    unittest.main()
