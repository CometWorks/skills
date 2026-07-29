#!/usr/bin/env python3
"""Code search smoke test for the decompiled code index.

Every check asserts its outcome: searches that must find something, searches
that must find nothing, and counts that must reach a lower bound. The runner
prints a summary and exits non-zero if any check failed, so a broken index or a
regression in the search script cannot pass unnoticed.

Run it through the platform wrapper (`test_search_*_code.sh` / `.bat`) so the
same checks run on Linux and Windows.
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()

# (kind, title, args) where kind is:
#   "any"    - must return at least one result
#   "none"   - must return NO-MATCHES
#   (min, N) - -c count must be at least N
CHECKS = [
    ("section", "CLASS DECLARATION", None),
    ("any", "MyPhysicsBody class declaration", ["class", "declaration", "MyPhysicsBody"]),
    ("any", "MyProjectorBase class declaration", ["class", "declaration", "MyProjectorBase"]),

    ("section", "CLASS USAGE", None),
    ("any", "MyPhysicsBody class usage (limit 5)", ["-l", "5", "class", "usage", "MyPhysicsBody"]),
    ("any", "MyProjectorBase class usage (limit 5)", ["-l", "5", "class", "usage", "MyProjectorBase"]),

    ("section", "STRUCT DECLARATION", None),
    ("any", "Vector3D struct declaration", ["struct", "declaration", "Vector3D"]),
    ("any", "Color struct declaration", ["struct", "declaration", "re:^Color$"]),

    ("section", "STRUCT USAGE", None),
    ("any", "Vector3D struct usage (limit 5)", ["-l", "5", "struct", "usage", "Vector3D"]),
    ("any", "Color struct usage (limit 5)", ["-l", "5", "struct", "usage", "re:^Color$"]),

    ("section", "METHOD DECLARATION", None),
    ("any", "Activate method declaration", ["-l", "5", "method", "declaration", "Activate"]),
    ("any", "Build method declaration (limit 5)", ["-l", "5", "method", "declaration", "re:^Build$"]),
    ("any", "Abs method in Vector3D (namespace filter)", ["-n", "VRageMath", "method", "declaration", "re:^Abs$"]),

    ("section", "METHOD USAGE", None),
    ("any", "Activate method usage (limit 5)", ["-l", "5", "method", "usage", "Activate"]),
    ("any", "ClampToByte method usage (limit 5)", ["-l", "5", "method", "usage", "ClampToByte"]),

    ("section", "FIELD DECLARATION", None),
    ("any", "AngularDamping field declaration", ["field", "declaration", "AngularDamping"]),
    ("any", "AllowScaling field declaration", ["field", "declaration", "AllowScaling"]),
    ("any", "Forward field declaration (limit 5)", ["-l", "5", "field", "declaration", "re:^Forward$"]),

    ("section", "FIELD USAGE", None),
    # `Forward` members (MatrixD.Forward and friends) are properties; the old
    # indexer misfiled property accesses as field usages, so this check moved
    # from the field to the property category when that was fixed.
    ("any", "Forward property usage (limit 5)", ["-l", "5", "property", "usage", "re:^Forward$"]),
    ("any", "AngularDamping field usage (limit 5)", ["-l", "5", "field", "usage", "AngularDamping"]),

    ("section", "INTERFACE DECLARATION", None),
    ("any", "IMyPhysics interface declaration", ["interface", "declaration", "IMyPhysics"]),
    ("any", "IPhysicsMesh interface declaration", ["interface", "declaration", "IPhysicsMesh"]),

    ("section", "INTERFACE USAGE", None),
    ("any", "IMyEntity interface usage (limit 5)", ["-l", "5", "interface", "usage", "IMyEntity"]),

    ("section", "ENUM DECLARATION", None),
    ("any", "MyPhysicsOption enum declaration", ["enum", "declaration", "MyPhysicsOption"]),
    ("any", "GridEffectType enum declaration", ["enum", "declaration", "GridEffectType"]),

    ("section", "ENUM USAGE", None),
    ("any", "MyPhysicsOption enum usage (limit 5)", ["-l", "5", "enum", "usage", "MyPhysicsOption"]),

    ("section", "ENUM MEMBER DECLARATION", None),
    ("any", "FactionShare enum member declaration", ["enum_member", "declaration", "re:^FactionShare$"]),
    # Enum members have no usage form of their own; the search must degrade to
    # NO-MATCHES instead of failing.
    ("none", "Enum member usage form does not exist", ["enum_member", "usage", "FactionShare"]),

    # Usage rows carry the enclosing namespace/type/method as context columns next
    # to the symbol itself. Matching the wrong column silently hides most member
    # usages (they sit inside method bodies) and invents matches on method names.
    ("section", "MEMBER USAGE RESOLVES THE MEMBER, NOT ITS ENCLOSING METHOD", None),
    ("any", "m_cubeBlocks field usage (usages inside method bodies)", ["field", "usage", "re:^m_cubeBlocks$"]),
    ("none", "CanHavePhysics is a method - must not appear as a field usage", ["field", "usage", "re:^CanHavePhysics$"]),
    ("any", "IsWorking property usage", ["property", "usage", "re:^IsWorking$"]),
    ("none", "InitIDs is a method - must not appear as a property usage", ["property", "usage", "re:^InitIDs$"]),
    (("min", 50), "MyPhysicsBody class usages include those inside methods", ["class", "usage", "re:^MyPhysicsBody$"]),

    ("section", "NAMESPACE FILTERING", None),
    ("any", "Classes in Sandbox.Engine.Physics namespace", ["-n", "Sandbox.Engine.Physics", "-l", "5", "class", "declaration", ""]),
    ("any", 'Methods in VRageMath namespace containing "Add"', ["-n", "VRageMath", "-l", "5", "method", "declaration", "Add"]),

    ("section", "PAGINATION (LIMIT AND OFFSET)", None),
    ("any", "First 3 Vector3D usages", ["-l", "3", "struct", "usage", "Vector3D"]),
    ("any", "Next 3 Vector3D usages (offset 3)", ["-l", "3", "-o", "3", "struct", "usage", "Vector3D"]),
    ("any", "Skip 6, show 3", ["-l", "3", "-o", "6", "struct", "usage", "Vector3D"]),

    ("section", "COUNT MODE", None),
    (("min", 1), "Count of MyPhysicsBody usages", ["class", "usage", "MyPhysicsBody"]),
    (("min", 1), "Count of Vector3D usages", ["struct", "usage", "Vector3D"]),
    (("min", 1), "Count of Activate method declarations", ["method", "declaration", "Activate"]),

    ("section", "REGEX PATTERNS", None),
    ("any", 'Classes starting with "MyPhysics"', ["-l", "5", "class", "declaration", "re:^MyPhysics"]),
    ("any", 'Methods ending with "Position" (limit 5)', ["-l", "5", "method", "declaration", "re:Position$"]),
    ("any", 'Structs matching "Vector[23]D"', ["struct", "declaration", "re:^Vector[23]D$"]),

    ("section", "MULTIPLE PATTERNS (AND logic)", None),
    ("any", 'Methods containing both "Get" and "Position"', ["-l", "5", "method", "declaration", "Get", "Position"]),

    ("section", "METHOD SIGNATURE SEARCH", None),
    ("any", "Activate method signature", ["-l", "5", "method", "signature", "Activate"]),
    ("any", "Build method signature (limit 5)", ["-l", "5", "method", "signature", "re:^Build$"]),
    ("any", "Abs method signature in VRageMath namespace", ["-n", "VRageMath", "method", "signature", "re:^Abs$"]),
    (("min", 1), "Count of GetPosition method signatures", ["method", "signature", "GetPosition"]),
    ("any", 'Signature containing both "Get" and "Position"', ["-l", "5", "method", "signature", "Get", "Position"]),

    ("section", "NON-MATCHING EXAMPLES", None),
    ("none", "Non-existent class", ["class", "declaration", "ThisClassDoesNotExist12345"]),
    ("none", "Non-existent method", ["method", "declaration", "ZzzNonExistentMethod999"]),
    ("none", "Non-matching regex", ["struct", "declaration", "re:^ZZZZZ.*XXXXX$"]),

    ("section", "HIERARCHY SEARCH - CLASS PARENT", None),
    ("any", "Find parent of MyGrid", ["class", "parent", "MyGrid"]),
    ("any", "Find parent of MyProjectorBase", ["class", "parent", "MyProjectorBase"]),

    ("section", "HIERARCHY SEARCH - CLASS CHILDREN", None),
    ("any", "Find children of MyEntity (limit 5)", ["-l", "5", "class", "children", "MyEntity"]),
    ("any", "Find children of MyTerminalBlock (limit 3)", ["-l", "3", "class", "children", "MyTerminalBlock"]),

    ("section", "HIERARCHY SEARCH - INTERFACE PARENT", None),
    ("any", "Find parent of IMyTerminalBlock", ["interface", "parent", "IMyTerminalBlock"]),
    ("any", "Find parent of IMyFunctionalBlock", ["interface", "parent", "IMyFunctionalBlock"]),

    ("section", "HIERARCHY SEARCH - INTERFACE CHILDREN", None),
    ("any", "Find children of IMyEntity (limit 5)", ["-l", "5", "interface", "children", "IMyEntity"]),
    ("any", "Find children of IMyCubeBlock (limit 3)", ["-l", "3", "interface", "children", "IMyCubeBlock"]),

    ("section", "HIERARCHY SEARCH - CLASS IMPLEMENTS", None),
    ("any", "Find interfaces implemented by MyTerminalBlock", ["class", "implements", "MyTerminalBlock"]),
    ("any", "Find interfaces implemented by MyGrid", ["class", "implements", "MyGrid"]),

    ("section", "HIERARCHY SEARCH - INTERFACE IMPLEMENTORS", None),
    ("any", "Find implementors of IMyEntity (limit 5)", ["-l", "5", "interface", "implementors", "IMyEntity"]),
    ("any", "Find implementors of IMyTerminalBlock (limit 5)", ["-l", "5", "interface", "implementors", "IMyTerminalBlock"]),

    ("section", "HIERARCHY SEARCH - COUNT MODE", None),
    (("min", 1), "Count children of MyEntity", ["class", "children", "MyEntity"]),
    (("min", 1), "Count implementors of IMyEntity", ["interface", "implementors", "IMyEntity"]),

    ("section", "HIERARCHY SEARCH - WITH NAMESPACE FILTER", None),
    ("any", "Find children of MyEntity in Sandbox.Game namespace", ["-n", "Sandbox.Game", "-l", "5", "class", "children", "MyEntity"]),
    ("any", "Find implementors of IMyEntity in VRage.Game.ModAPI namespace", ["-n", "VRage.Game.ModAPI", "-l", "3", "interface", "implementors", "IMyEntity"]),
]

BANNER = "=" * 60


def find_search_script():
    """Locate the skill's search script (search_game_code.py / search_server_code.py)."""
    candidates = sorted(SCRIPT_DIR.glob("search_*_code.py"))
    if not candidates:
        print(f"FATAL: no search_*_code.py found in {SCRIPT_DIR}")
        sys.exit(2)
    return candidates[0]


def section(title):
    print(BANNER)
    print(title)
    print(BANNER)


def run_search(script, args):
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    return (result.stdout + result.stderr).strip()


def main():
    script = find_search_script()
    checks = 0
    failures = []

    for kind, title, args in CHECKS:
        if kind == "section":
            section(title)
            continue

        checks += 1
        is_count_check = kind not in ("any", "none")

        print(f"--- {title} ---")
        output = run_search(script, ["-c", *args] if is_count_check else args)
        print(output)

        problem = None
        if kind == "any":
            if not output or output == "NO-MATCHES":
                problem = "expected at least one result"
        elif kind == "none":
            if output != "NO-MATCHES":
                problem = "expected NO-MATCHES"
        else:
            minimum = kind[1]
            if not output.isdigit():
                problem = f"expected a count, got {output!r}"
            elif int(output) < minimum:
                problem = f"expected count >= {minimum}, got {output}"

        if problem:
            print(f"FAIL: {problem}")
            failures.append(f"{title}: {problem}")
        print()

    section("SUMMARY")
    print(f"Checks run: {checks}")
    print(f"Failures:   {len(failures)}")
    print()
    if failures:
        for failure in failures:
            print(f"FAILED - {failure}")
        print()
        section("TESTS FAILED")
        return 1

    section("ALL TESTS COMPLETED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
