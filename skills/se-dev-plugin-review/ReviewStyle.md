# Review Style and Evidence Provenance

Use the evidence-led review style established by Viktor Ferenczi's PluginHub reviews. These are style and provenance exemplars, not reusable conclusions:

- [PluginHub #190 review](https://github.com/StarCpt/PluginHub/pull/190#pullrequestreview-5148515134): new-plugin manifest, security, loader compilation, decompiled-game verification, and cross-plugin compatibility.
- [PluginHub #175 review](https://github.com/StarCpt/PluginHub/pull/175#pullrequestreview-5123575330): repository reachability, network/privacy disclosure, dependency licensing, performance, and maintainer questions.
- [PluginHub #177 initial review](https://github.com/StarCpt/PluginHub/pull/177#pullrequestreview-5123542554): multiple manifests, native-binary authentication, current-loader behavior, upstream source licensing, and per-plugin recommendations.
- [PluginHub #177 re-review](https://github.com/StarCpt/PluginHub/pull/177#pullrequestreview-5127408225): fresh pins, prior-finding disposition, asset re-verification, and explicit runtime-test gaps.
- [PluginHub #187 bump review](https://github.com/StarCpt/PluginHub/pull/187#pullrequestreview-5127210828): exact old/new range, delta size, preservation of prior security conditions, loader-real compilation, and non-blocking residual risks.

Do not impersonate Viktor, attribute the review to him, or copy his conclusions. Reproduce the evidentiary standard and readable structure using facts independently verified for the current PR.

## Review body

Open with exact scope: hub PR head, target repository, pinned source SHA or old/new range, and whether this is a full-repository review or bump re-review. Then give a short summary stating blockers and material residual risks without claiming human approval.

Use only relevant sections, normally selected from:

- `Manifest`
- `Repository and pin provenance`
- `Security`
- `From-source build`
- `Compatibility / authority`
- `Findings` or per-plugin findings
- `Non-blocking notes`

Order blocking findings before lower-severity notes. Use `Blocking`, `High`, `Medium`, `Low`, or `Note`; explain why the severity fits. A finding should identify evidence, the causal path, user/runtime consequence, concrete fix, and important tradeoff. Link source evidence to the exact reviewed commit and line range.

Include useful positive evidence. State why suspicious-looking code is benign when that distinction matters, such as reflection over fixed types, legitimate native interop, or client-only behavior with no concrete server-authority bypass.

Keep the human-only checklist and general verification limitations outside the GitHub review body. Do not add a `Verification gaps` section or end with human-manual-review/approval boilerplate. If an unverified fact is itself material to an author-actionable finding—such as binary provenance that cannot be established—state that uncertainty inside the relevant finding rather than hiding it.

## Provenance standard

Make every important claim reproducible:

- Give exact full source pins/ranges and tags when verified. Check whether a pin is reachable from the repository's default branch and whether repository HEAD differs; inspect and classify any drift.
- State the exact validator/build command or material settings and its result. Loader-real compilation takes precedence over an IDE build.
- Name the current loader source/member or game type/member used to verify host behavior. Cite a commit or installed version; distinguish source verification from inference.
- For dependencies, establish source, exact version, license when relevant, actual source usage, and whether the loader supplies/restores/loads it.
- For committed or remotely downloaded binaries, record size, SHA-256, version/signature metadata when available, and the authoritative upstream artifact used for byte comparison. If authenticity cannot be established, say so.
- Enumerate actual network destinations and data sent, filesystem roots and written data, process/shell behavior, dynamic-code paths, native interop, credential/identifier handling, and obfuscation/decoded payload findings.
- For compatibility claims, name the compared plugin/repository pin or host implementation and trace the concrete shared hook, UI control, file, state, or lifecycle interaction.
- On a re-review, re-fetch the PR head and source pins, list each prior material finding as fixed, remaining, regressed, or unable to verify, and re-run affected provenance checks.
- Quantify scope where useful: repository path count for new registrations; changed paths and insertion/deletion counts for bumps; source LOC; compiler warning/error counts.

Never turn a grep result, successful build, repository ownership, signature, or prior review into a general safety claim. Separate `verified`, `not present in reviewed scope`, `not run`, and `unable to verify`.

## Authority and tone

Write as a technical peer: direct, specific, and explanatory. Thanking the author is optional. Praise only work directly verified and relevant to the gate. Correct prior mistakes transparently.

Do not use Viktor's authority or GitHub review decision as provenance. The agent produces a preview and may state `No agent-detected blockers`; only the human reviewer decides approval or request-changes state. If caveman mode is active, keep chat updates compressed but do not compress the GitHub review artifact below this evidence standard.
