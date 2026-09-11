# New Registration and Version-Bump Paths

Use the `review_type` emitted by the preparation script. Security is mandatory in both paths; light means narrow scope, not cursory reading.

## New registration — heavy

Audit the complete executable and build closure at `new_source_sha`.

1. Inventory the pinned tree, submodules, symlinks, LFS objects, archives, committed binaries/native files, packages, restore sources, build targets, scripts, generated code, and assets. Audit pinned submodule content separately; do not assume the parent diff covers it.
2. Read every source file compiled or loaded by the hub plus project references/imports and code generators affecting output.
3. Trace every sensitive control/data flow in [ReviewPolicy.md](ReviewPolicy.md), enumerate network destinations, and establish filesystem boundaries.
4. Establish the full authority/capability boundary. For game plugins, compare it with vanilla multiplayer limits.
5. Verify lifecycle cleanup, plugin compatibility, hot-path cost, threading, persistence, and failure behavior.
6. Validate manifest claims and ensure source/build selection excludes unrelated tests or tooling.
7. Build through the hub/loader's real source path and load-test when available. State exact gaps when unavailable.

The manual-review block must guide the human through the highest-risk files and decisions across the complete plugin.

## Version bump — light and exact

Start from generated `source.diff`, exactly:

`git diff <old_source_sha>..<new_source_sha>`

1. Enumerate changed paths and read the complete diff line by line.
2. Read unchanged context only to understand changed behavior, callers, data origins/sinks, API contracts, and lifecycle effects.
3. Inspect changed package/build files and newly added managed/native binaries explicitly. Expand dependency provenance only where the diff changes it.
4. Apply security, authority/fairness, filesystem, performance, compatibility, and maintainability rules to changed behavior. Do not re-audit unrelated unchanged code.
5. Build pinned head through the relevant source-build path when available.

If source-selection or project-reference changes expose previously excluded code, review that newly included closure at new-registration depth. If the direct diff is unexpectedly huge, report scope expansion instead of pretending a light review is complete.

The manual-review block should name only changed high-risk code and decisions, plus explicit package/native-file status.

## Other script results

- `metadata_only`: review only hub metadata; do not invent a source diff.
- `removal`: review removal/dependency impact; there is no target source audit.
- Changed `<RepoId>`: treat head repository as `new_registration` and highlight the identity change.
