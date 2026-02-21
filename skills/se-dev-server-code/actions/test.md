# Test Action

> **Part of the se-dev-server-code skill.** Invoked to run server code search tests and verify results.

Run `test_search.bat` to verify the server code search functionality is working correctly.

## Running Tests

From this skill folder, run:

```cmd
.\test_search.bat
```

Or redirect output to a file for review:

```cmd
.\test_search.bat > test_results.txt 2>&1
```

## What the Tests Cover

The test suite exercises all server code search capabilities:

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
| Count mode | counting results instead of listing |
| Regex patterns | ^MyPhysics, Position$, Vector[23]D |
| Multiple patterns | AND logic with multiple terms |
| Hierarchy - class parent | MyGrid, MyProjectorBase |
| Hierarchy - class children | MyEntity, MyTerminalBlock |
| Hierarchy - interface parent | IMyTerminalBlock, IMyFunctionalBlock |
| Hierarchy - interface children | IMyEntity, IMyCubeBlock |
| Hierarchy - class implements | MyTerminalBlock, MyGrid |
| Hierarchy - interface implementors | IMyEntity, IMyTerminalBlock |
| Non-matching examples | Verify empty results don't crash |

## Verifying Results

A successful test run should:

1. **Complete without errors** - No Python exceptions or crashes
2. **Return results for known items** - Each search (except non-matching examples) should return at least one result
3. **Show "No results found"** for the non-matching examples section
4. **End with "ALL TESTS COMPLETED"** message

## Example Verification

Check that key searches return expected results:

```cmd
REM Should find the MyPhysicsBody class
uv run search_code.py class declaration MyPhysicsBody

REM Should find Vector3D struct
uv run search_code.py struct declaration Vector3D

REM Should return count > 0
uv run search_code.py -c class usage MyPhysicsBody
```

## Troubleshooting

If tests fail:

1. **Preparation not complete** - Run `.\Prepare.bat` first
2. **Index not built** - Check that `CodeIndex/` folder exists and contains `.json` files
3. **Decompiled folder missing** - Verify `Decompiled/` folder has `.cs` files
4. **Python environment issues** - Try `uv sync` to reinstall dependencies

As a last resort, you can force repeating the whole preparation process by running `.\Clean.bat`, then `.\Prepare.bat`.
Notify the user if you do this, because the preparation may take 5-15 minutes to complete depending on the hardware.
