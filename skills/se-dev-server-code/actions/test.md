# Test Action

> **Part of the se-dev-server-code skill.** Invoked to run server code search tests and verify results.

Run the test script to verify server code search works correctly.

## Running Tests

From this skill folder, run:

```bash
# Linux
./test_search_server_code.sh
```

```cmd
REM Windows
.\test_search_server_code.bat
```

Or redirect output to file for review:

```bash
# Linux
./test_search_server_code.sh > test_results.txt 2>&1
```

```cmd
REM Windows
.\test_search_server_code.bat > test_results.txt 2>&1
```

Both wrappers run the same checks from `test_search_code.py`, so Linux and
Windows results are identical.

## What the Tests Cover

Test suite exercises all server code search capabilities:

| Category | Tests |
|----------|-------|
| Class declaration | MyPhysicsBody, MyProjectorBase |
| Class usage | MyPhysicsBody, MyProjectorBase |
| Struct declaration | Vector3D, Color |
| Struct usage | Vector3D, Color |
| Method declaration | Activate, Build, Abs |
| Method usage | Activate, ClampToByte |
| Method signature | Activate, Build, Abs, GetPosition |
| Field declaration | AngularDamping, AllowScaling, Forward |
| Field usage | Forward, AngularDamping |
| Interface declaration | IMyPhysics, IPhysicsMesh |
| Interface usage | IMyEntity |
| Enum declaration | MyPhysicsOption, GridEffectType |
| Enum usage | MyPhysicsOption |
| Namespace filtering | Sandbox.Engine.Physics, VRageMath |
| Pagination | limit and offset options |
| Count mode | count results instead of listing |
| Regex patterns | ^MyPhysics, Position$, Vector[23]D |
| Multiple patterns | AND logic with multiple terms |
| Hierarchy - class parent | MyGrid, MyProjectorBase |
| Hierarchy - class children | MyEntity, MyTerminalBlock |
| Hierarchy - interface parent | IMyTerminalBlock, IMyFunctionalBlock |
| Hierarchy - interface children | IMyEntity, IMyCubeBlock |
| Hierarchy - class implements | MyTerminalBlock, MyGrid |
| Hierarchy - interface implementors | IMyEntity, IMyTerminalBlock |
| Member usage vs enclosing method | m_cubeBlocks, CanHavePhysics, IsWorking, InitIDs |
| Non-matching examples | Verify empty results don't crash |

## Verifying Results

Each check asserts its own outcome, so reading the output is optional - exit
code is authoritative:

- **Exit code 0** and a final `ALL TESTS COMPLETED` banner - everything passed
- **Exit code 1**, `FAIL:` lines next to failing checks and a `TESTS FAILED`
  banner - the `SUMMARY` section lists every failure

Searches finding nothing print `NO-MATCHES`, expected only in non-matching
examples section and in checks asserting a symbol must *not* be found.

## Example Verification

Check key searches return expected results:

```bash
# Should find MyPhysicsBody class
uv run search_server_code.py class declaration MyPhysicsBody

# Should find Vector3D struct
uv run search_server_code.py struct declaration Vector3D

# Should return count > 0
uv run search_server_code.py -c class usage MyPhysicsBody
```

## Troubleshooting

If tests fail:

1. **Preparation not complete** - Run `./prepare.sh` (Linux) or `.\Prepare.bat` (Windows) first
2. **Index not built** - Check `Data/CodeIndex/` exists and contains `.csv` files
3. **Decompiled folder missing** - Verify `Data/Decompiled/` has `.cs` files
4. **Python environment issues** - Try `uv sync` to reinstall dependencies

As last resort, force repeating whole preparation process by running `./clean.sh` then `./prepare.sh`
(Linux), or `.\Clean.bat` then `.\Prepare.bat` (Windows).
Notify user if you do this, because preparation may take 5-15 minutes depending on hardware.

## Optional: Graphify Graph Test

If the optional Graphify graph was built (see [Optional Graphify Graph](../SKILL.md) and
[GraphifyPrepare.md](../../se-dev/GraphifyPrepare.md)), verify it separately with the graph
query smoke test — analogous to the code-search test but exercising the Graphify graph:

```bash
# Linux
./test_graphify_server_code.sh
```

```cmd
REM Windows
.\test_graphify_server_code.bat
```

It first runs a health check (graph built and clustered), then asserted
`query`/`explain`/`path`/`affected` calls, ending with `ALL TESTS COMPLETED` and exit code 0.
If it stops at the health check, the graph is missing or unusable (clustering not finished);
rebuild it with `SE_DEV_GRAPHIFY=1` after confirming the ~10-30 minute cost with the user.

An `explain` check fails when the name resolves to a node without a source location. That
means Graphify's fuzzy matching settled on a stub node instead of the real symbol - see
[GraphifyUsage.md](../../se-dev/GraphifyUsage.md#name-resolution-pitfalls).
