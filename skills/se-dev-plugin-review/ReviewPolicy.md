# Plugin Review Policy

Use judgment, not keyword matching. Plugins execute unsandboxed with the user's or server's authority, so code must remain understandable enough to audit.

## Security and supply chain

- Manually trace every in-scope path involving dynamic assembly/code loading, reflection driven by external input, process execution, shell commands, networking, credentials, identifiers, local files, serialization, cryptography, or decoded/compressed payloads.
- Enumerate every contacted host and the data sent. Reject unexplained telemetry, exfiltration, remote-controlled commands, or hidden endpoints.
- Inspect new or changed package references, lock files, restore sources, build targets, scripts, and generated code. Confirm each dependency is necessary and that registry metadata supplies dependencies needed by the loader's source compiler.
- Reject unexplained committed executables, managed DLLs, or native libraries. If an exceptional binary is necessary, establish its authoritative origin and verify it byte-for-byte; unverifiable code is not reviewable.
- Reject self-updating code. Registry commit pins and the loader owns updates.
- Reject obfuscation, encoded indirection, or spaghetti that prevents confident review.
- AI/scanner output can direct attention but cannot replace reading the actual source. The human maintainer owns final security judgment and approval.

## Multiplayer fairness

Ask what information or action a vanilla player could obtain in the same situation.

- If vanilla provides no legitimate route to the information or action, presume the feature is too cheaty for multiplayer until a convincing, enforceable justification is demonstrated.
- Check ownership, relation, access, safe-zone, visibility, replication, spectator, camera, voxel, ore, inventory, entity, and remote-control boundaries relevant to the feature.
- Client-side UI or input gates are not server authority. Do not treat them as enforcement when a modified client can bypass them.
- Automation and presentation are not automatically cheating; judge whether they reveal hidden state, bypass gameplay constraints, or perform actions beyond the player's legitimate authority.
- When fairness is ambiguous, ask a short, concrete question describing the exact vanilla comparison and multiplayer consequence.

## Filesystem and persistence

- Use `MyFileSystem.UserDataPath` for user data. Do not use `Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)` because Space Engineers supports the `-appdata` launch argument.
- Do not modify installed game files or mod files on disk. Removing a misbehaving plugin must be enough to stop its persistent effects.
- Keep configuration and generated data under a plugin-owned location beneath the game user-data path.
- Treat arbitrary file access, broad path traversal, insecure temporary files, and non-atomic destructive writes as security or data-loss risks.

## Compatibility, performance, and maintainability

- Do not clobber other plugins: use unique Harmony IDs, narrow patch targets, undo registrations/patches on dispose, preserve shared state, and avoid replacing global handlers when composition is possible.
- Do not noticeably degrade performance without a feature-level reason. Inspect hot hooks for repeated reflection, allocation, logging, scans, locks, blocking I/O, unbounded queues, and unsafe background access to game objects.
- Fail safely across lifecycle transitions: world load/unload, reconnect, dedicated/client differences, null singleton windows, partial initialization, and plugin disable/reload.
- Prefer direct, boring code. Flag needless complexity only when it increases audit cost, bug risk, or compatibility risk; omit taste-only feedback.
- Swallowed exceptions are acceptable only for narrowly understood, genuinely optional behavior. Otherwise preserve enough context to diagnose failure.

## Evidence and stopping rules

- Distinguish `verified`, `not present in the reviewed scope`, `not run`, and `unable to verify`.
- A normal build does not prove loader compilation or runtime loading.
- Absence of a search hit does not prove absence of a security issue.
- Unavailable source, mismatched pins, unexplained binaries, or security-critical behavior that cannot be understood are blockers, not assumptions to waive.
- Keep feedback short, but do not compress away threat model, exploitability, affected data, or required remediation for a security finding.
