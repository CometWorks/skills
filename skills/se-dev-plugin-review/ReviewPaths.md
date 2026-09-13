# New Registration and Version-Bump Paths

Use the `review_type` emitted by the preparation script. Security is mandatory in both paths; light means narrow scope, not cursory reading.

## New registration — full repository gate

Require `source.audit_scope == full_repository_tree` and use `source-tree.txt`. Audit every tracked path in the repository at `new_source_sha`, not merely the manifest-selected source, latest commit, executable closure, or files that look relevant. Do not generate or use a diff for this path.

1. Account for every path in `source-tree.txt`. Read every text/source/configuration file; inspect binary/assets using format-appropriate tools and establish provenance where required. Record exact unreadable or unevaluated paths as blockers or manual-review gaps.
2. Inventory the pinned tree, submodules, symlinks, LFS objects, archives, committed binaries/native files, packages, restore sources, build targets, scripts, generated code, assets, tests, examples, tooling, and documentation. Audit pinned submodule content separately; do not assume the parent inventory covers it.
3. Establish what the hub compiles or loads, but do not use that narrower closure to skip repository files. Audit every assembly, project, package, framework, COM, and analyzer reference declared by project files or imported props/targets; follow the provenance and usage rules in [ReviewPolicy.md](ReviewPolicy.md). Read code generators affecting output.
4. Trace every sensitive control/data flow in [ReviewPolicy.md](ReviewPolicy.md), enumerate network destinations, and establish filesystem boundaries.
5. Establish the full authority/capability boundary. For game plugins, compare it with vanilla multiplayer limits.
6. Verify lifecycle cleanup, plugin compatibility, hot-path cost, threading, persistence, and failure behavior.
7. Validate manifest claims and ensure source/build selection excludes unrelated tests or tooling.
8. Build through the hub/loader's real source path and load-test when available. State exact gaps when unavailable.

The performed-checks summary must state the repository path count and confirm every path was accounted for, or name all gaps. The manual-review block must guide the human through the highest-risk files and decisions across the complete repository, with explicit project-reference, package, and native-file status. An unaccounted path fails this gate.

## Version bump — light and exact

Require `source.audit_scope == direct_commit_diff`. Only on this script-selected path, start from generated `source.diff`, exactly:

`git diff <old_source_sha>..<new_source_sha>`

1. Use the programmatic diff artifact, enumerate changed paths, and read the complete diff line by line. Do not substitute GitHub's displayed patch, a latest-commit diff, or a default-branch comparison.
2. Read unchanged context only to understand changed behavior, callers, data origins/sinks, API contracts, and lifecycle effects.
3. Inspect changed package/build files, assembly/project references, and newly added managed/native binaries explicitly. Expand dependency provenance only where the diff changes it. A reference change that exposes previously excluded source or executable code expands that closure to new-registration depth.
4. Apply security, authority/fairness, filesystem, performance, compatibility, and maintainability rules to changed behavior. Do not re-audit unrelated unchanged code.
5. Build pinned head through the relevant source-build path when available.

If source-selection or project-reference changes expose previously excluded code, review that newly included closure at new-registration depth. If the direct diff is unexpectedly huge, report scope expansion instead of pretending a light review is complete.

The manual-review block should name only changed high-risk code and decisions, plus explicit project-reference, package, and native-file status.

## Other script results

- `metadata_only`: review only hub metadata; do not invent a source diff.
- `removal`: review removal/dependency impact; there is no target source audit.
- Changed `<RepoId>`: treat head repository as `new_registration` and highlight the identity change.
