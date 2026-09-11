#!/usr/bin/env python3
"""Prepare reproducible review artifacts from a supported plugin-hub PR."""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote, urlparse


REPO_ID = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PACKAGE_FILES = {
    "directory.packages.props",
    "packages.lock.json",
    "nuget.config",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}
BINARY_SUFFIXES = {".dll", ".exe", ".nupkg", ".wasm", ".zip", ".7z", ".rar", ".gz"}
NATIVE_SUFFIXES = {".so", ".dylib", ".a", ".lib", ".node"}
BUILD_SUFFIXES = {".csproj", ".fsproj", ".vbproj", ".sln", ".props", ".targets", ".sh", ".bat", ".cmd", ".ps1"}


class ReviewError(RuntimeError):
    pass


def run(args: list[str], cwd: Path | None = None, input_text: str | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, text=True, input=input_text, capture_output=True)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ReviewError(f"Command failed ({' '.join(args)}): {detail}")
    return result.stdout


def gh_json(endpoint: str, fields: dict[str, str] | None = None) -> object:
    args = ["gh", "api", "--method", "GET", endpoint]
    for key, value in (fields or {}).items():
        args.extend(["-f", f"{key}={value}"])
    return json.loads(run(args))


def gh_text(endpoint: str, accept: str) -> str:
    return run(["gh", "api", endpoint, "-H", f"Accept: {accept}"])


def parse_pr_url(value: str, supported_hubs: set[str]) -> tuple[str, int]:
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ReviewError("Expected an https://github.com/<owner>/<repo>/pull/<number> URL")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 4 or parts[2] != "pull" or not parts[3].isdigit():
        raise ReviewError("Expected an https://github.com/<owner>/<repo>/pull/<number> URL")
    repo = f"{parts[0]}/{parts[1]}"
    if repo.lower() not in {hub.lower() for hub in supported_hubs}:
        raise ReviewError(f"Unsupported hub {repo}; expected one of {sorted(supported_hubs)}")
    canonical = next(hub for hub in supported_hubs if hub.lower() == repo.lower())
    return canonical, int(parts[3])


def get_pr_files(repo: str, number: int) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    page = 1
    while True:
        batch = gh_json(
            f"repos/{repo}/pulls/{number}/files",
            {"per_page": "100", "page": str(page)},
        )
        if not isinstance(batch, list):
            raise ReviewError("GitHub returned an invalid PR file list")
        files.extend(batch)
        if len(batch) < 100:
            return files
        page += 1


def get_file(repo: str, path: str, commit: str) -> bytes:
    encoded_path = quote(path, safe="/")
    result = gh_json(f"repos/{repo}/contents/{encoded_path}", {"ref": commit})
    if not isinstance(result, dict) or result.get("encoding") != "base64":
        raise ReviewError(f"GitHub did not return base64 file content for {repo}:{path}@{commit}")
    return base64.b64decode(str(result["content"]), validate=False)


def parse_manifest(data: bytes, label: str) -> dict[str, object]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError as error:
        raise ReviewError(f"Invalid XML in {label}: {error}") from error

    def text(name: str) -> str | None:
        element = root.find(name)
        if element is None or element.text is None:
            return None
        value = element.text.strip()
        return value or None

    def values(path: str) -> list[str]:
        return [element.text.strip() for element in root.findall(path) if element.text and element.text.strip()]

    return {
        "id": text("Id"),
        "repo_id": text("RepoId"),
        "commit": text("Commit"),
        "friendly_name": text("FriendlyName"),
        "source_directories": values("SourceDirectories/Directory"),
        "asset_folder": text("AssetFolder"),
        "project_path": text("ProjectPath"),
        "package_manifest": text("PackageManifest"),
        "plugin_kind": text("PluginKind"),
        "platforms": text("Platforms"),
        "runtimes": text("Runtimes"),
        "implicit_loading": text("ImplicitLoading"),
        "dependencies": values("DependencyIds/Id"),
        "companion_plugins": values("CompanionPluginIds/Id"),
        "nuget_references": [
            {"include": element.get("Include"), "version": element.get("Version")}
            for element in root.findall("NuGetReferences/PackageReference")
        ],
        "nuget_config": text("NuGetReferences/Config"),
        "alternate_versions": [
            {"name": version.findtext("Name"), "commit": version.findtext("Commit")}
            for version in root.findall("AlternateVersions/Version")
        ],
    }


def resolve_commit(repo: str, pin: str) -> str:
    result = gh_json(f"repos/{repo}/commits/{quote(pin, safe='')}")
    if not isinstance(result, dict) or not re.fullmatch(r"[0-9a-f]{40}", str(result.get("sha", ""))):
        raise ReviewError(f"Could not resolve {repo}@{pin} to a full commit SHA")
    return str(result["sha"])


def validate_manifest(manifest: dict[str, object], review_family: str, path: str) -> None:
    if review_family != "quasar":
        return
    if manifest.get("plugin_kind") != "QuasarUiPlugin":
        raise ReviewError(f"Invalid PluginKind in {path}; expected QuasarUiPlugin")
    if not manifest.get("project_path") or not manifest.get("package_manifest"):
        raise ReviewError(f"QuasarHub manifest {path} requires ProjectPath and PackageManifest")


def classify(paths: list[str]) -> dict[str, list[str]]:
    packages, binaries, native, build = [], [], [], []
    for item in paths:
        path = Path(item)
        lower_name = path.name.lower()
        suffix = path.suffix.lower()
        if lower_name in PACKAGE_FILES or lower_name.endswith(".lock.json"):
            packages.append(item)
        if suffix in BINARY_SUFFIXES:
            binaries.append(item)
        if suffix in NATIVE_SUFFIXES:
            native.append(item)
        if suffix in BUILD_SUFFIXES or lower_name in {"dockerfile", "makefile"}:
            build.append(item)
    return {
        "package_files": packages,
        "binary_files": binaries,
        "native_files": native,
        "build_files": build,
    }


def write(path: Path, data: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, bytes):
        path.write_bytes(data)
    else:
        path.write_text(data, encoding="utf-8")


def prepare_source(
    directory: Path,
    repo: str,
    old_sha: str | None,
    new_sha: str,
    review_type: str,
) -> dict[str, object]:
    source = directory / "source"
    expected_url = f"https://github.com/{repo}.git"
    created = not source.exists()
    if created:
        run(["git", "clone", "--no-checkout", expected_url, str(source)])
    elif not (source / ".git").exists():
        raise ReviewError(f"Refusing to reuse non-repository path {source}")
    else:
        actual_url = run(["git", "remote", "get-url", "origin"], source).strip()
        normalized = actual_url.removesuffix(".git").lower()
        if normalized != expected_url.removesuffix(".git").lower():
            raise ReviewError(f"Refusing to reuse {source}; origin is {actual_url}, expected {expected_url}")

    if not created and run(["git", "status", "--porcelain"], source).strip():
        raise ReviewError(f"Refusing to update dirty review checkout {source}")

    run(["git", "fetch", "--no-tags", "origin", new_sha], source)
    if old_sha:
        run(["git", "fetch", "--no-tags", "origin", old_sha], source)
    run(["git", "switch", "--detach", new_sha], source)

    tree_lines = run(["git", "ls-tree", "-r", "--full-tree", new_sha], source).splitlines()
    tree_paths: list[str] = []
    submodules: list[dict[str, str]] = []
    symlinks: list[str] = []
    for line in tree_lines:
        metadata, path = line.split("\t", 1)
        mode, object_type, object_sha = metadata.split()
        tree_paths.append(path)
        if mode == "160000" or object_type == "commit":
            submodules.append({"path": path, "commit": object_sha})
        if mode == "120000":
            symlinks.append(path)

    if review_type == "version_bump" and old_sha:
        diff = run(["git", "diff", "--binary", "--find-renames", f"{old_sha}..{new_sha}"], source)
        name_status = run(["git", "diff", "--name-status", "--find-renames", f"{old_sha}..{new_sha}"], source)
        changed_paths = []
        for line in name_status.splitlines():
            columns = line.split("\t")
            changed_paths.append(columns[-1])
        write(directory / "source.diff", diff)
        write(directory / "changed-files.txt", name_status)
        scope_paths = changed_paths
    else:
        write(directory / "source-tree.txt", "\n".join(tree_paths) + "\n")
        scope_paths = tree_paths

    return {
        "checkout": str(source.resolve()),
        "review_type": review_type,
        "old_source_sha": old_sha,
        "new_source_sha": new_sha,
        "scope_file_count": len(scope_paths),
        "submodules": submodules,
        "symlinks": symlinks,
        **classify(scope_paths),
    }


def safe_name(index: int, path: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "-", Path(path).stem).strip("-.") or "plugin"
    return f"{index:02d}-{stem}"


def prepare(pr_url: str, output_arg: Path | None, supported_hubs: set[str], review_family: str) -> int:
    try:
        hub_repo, number = parse_pr_url(pr_url, supported_hubs)
        default_name = f"{hub_repo.replace('/', '-')}-pr-{number}"
        output = (output_arg or Path.home() / ".se-dev" / "reviews" / default_name).resolve()
        output.mkdir(parents=True, exist_ok=True)

        pr = gh_json(f"repos/{hub_repo}/pulls/{number}")
        if not isinstance(pr, dict):
            raise ReviewError("GitHub returned invalid PR metadata")
        base_repo = str(pr["base"]["repo"]["full_name"])
        head_repo = str(pr["head"]["repo"]["full_name"])
        base_sha = str(pr["base"]["sha"])
        head_sha = str(pr["head"]["sha"])
        files = get_pr_files(hub_repo, number)
        manifest_changes = [
            file for file in files
            if str(file.get("filename", "")).startswith("Plugins/")
            and str(file.get("filename", "")).lower().endswith(".xml")
        ]
        if not manifest_changes:
            raise ReviewError("PR changes no XML manifest beneath Plugins/")

        write(
            output / "hub.diff",
            gh_text(f"repos/{hub_repo}/pulls/{number}", "application/vnd.github.v3.diff"),
        )

        reviews: list[dict[str, object]] = []
        for index, change in enumerate(manifest_changes, start=1):
            status = str(change.get("status", ""))
            head_path = str(change["filename"])
            base_path = str(change.get("previous_filename", head_path))
            review_dir = output / "plugins" / safe_name(index, head_path)

            base_data = None if status == "added" else get_file(base_repo, base_path, base_sha)
            head_data = None if status == "removed" else get_file(head_repo, head_path, head_sha)
            if base_data is not None:
                write(review_dir / "manifest.base.xml", base_data)
            if head_data is not None:
                write(review_dir / "manifest.head.xml", head_data)

            base_manifest = parse_manifest(base_data, f"{base_path}@{base_sha}") if base_data else None
            head_manifest = parse_manifest(head_data, f"{head_path}@{head_sha}") if head_data else None
            review: dict[str, object] = {
                "manifest_path": head_path,
                "hub_change_status": status,
                "base_manifest": base_manifest,
                "head_manifest": head_manifest,
            }

            if head_manifest is None:
                review["review_type"] = "removal"
            else:
                validate_manifest(head_manifest, review_family, head_path)
                repo_id = str(head_manifest.get("repo_id") or "")
                new_pin = str(head_manifest.get("commit") or "")
                if not REPO_ID.fullmatch(repo_id):
                    raise ReviewError(f"Invalid or missing RepoId in {head_path}: {repo_id!r}")
                if not new_pin:
                    raise ReviewError(f"Missing Commit in {head_path}")

                old_repo = str((base_manifest or {}).get("repo_id") or "")
                old_pin = str((base_manifest or {}).get("commit") or "")
                if base_manifest is None or old_repo.lower() != repo_id.lower():
                    review_type = "new_registration"
                    old_full = None
                elif old_pin == new_pin:
                    review_type = "metadata_only"
                    old_full = None
                else:
                    review_type = "version_bump"
                    old_full = resolve_commit(repo_id, old_pin)

                new_full = resolve_commit(repo_id, new_pin)
                review.update({
                    "review_type": review_type,
                    "target_repo": repo_id,
                    "old_source_pin": old_pin or None,
                    "new_source_pin": new_pin,
                    "old_source_sha": old_full,
                    "new_source_sha": new_full,
                })
                if review_type != "metadata_only":
                    review["source"] = prepare_source(review_dir, repo_id, old_full, new_full, review_type)

            write(review_dir / "review.json", json.dumps(review, indent=2, sort_keys=True) + "\n")
            reviews.append(review)

        bundle = {
            "schema_version": 1,
            "review_family": review_family,
            "pr_url": str(pr["html_url"]),
            "hub_repo": hub_repo,
            "pr_number": number,
            "pr_state": pr.get("state"),
            "pr_title": pr.get("title"),
            "hub_base_sha": base_sha,
            "hub_head_sha": head_sha,
            "manifest_count": len(reviews),
            "reviews": reviews,
        }
        write(output / "review.json", json.dumps(bundle, indent=2, sort_keys=True) + "\n")

        print(f"Prepared {len(reviews)} review(s) for {hub_repo}#{number} at {output}")
        for review in reviews:
            target = review.get("target_repo", "-")
            old_sha = review.get("old_source_sha") or "-"
            new_sha = review.get("new_source_sha") or "-"
            print(f"{review['manifest_path']}: {review['review_type']} {target} {old_sha}..{new_sha}")
        return 0
    except (KeyError, OSError, ReviewError, subprocess.SubprocessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
