@echo off
setlocal
cd /d "%~dp0"

echo ============================================================
echo CLASS DECLARATION
echo ============================================================
echo --- MyPhysicsBody class declaration ---
uv run search_code.py class declaration MyPhysicsBody
echo.
echo --- MyProjectorBase class declaration ---
uv run search_code.py class declaration MyProjectorBase
echo.

echo ============================================================
echo CLASS USAGE
echo ============================================================
echo --- MyPhysicsBody class usage (limit 5) ---
uv run search_code.py -l 5 class usage MyPhysicsBody
echo.
echo --- MyProjectorBase class usage (limit 5) ---
uv run search_code.py -l 5 class usage MyProjectorBase
echo.

echo ============================================================
echo STRUCT DECLARATION
echo ============================================================
echo --- Vector3D struct declaration ---
uv run search_code.py struct declaration Vector3D
echo.
echo --- Color struct declaration ---
uv run search_code.py struct declaration "re:^Color$"
echo.

echo ============================================================
echo STRUCT USAGE
echo ============================================================
echo --- Vector3D struct usage (limit 5) ---
uv run search_code.py -l 5 struct usage Vector3D
echo.
echo --- Color struct usage (limit 5) ---
uv run search_code.py -l 5 struct usage "re:^Color$"
echo.

echo ============================================================
echo METHOD DECLARATION
echo ============================================================
echo --- Activate method declaration ---
uv run search_code.py -l 5 method declaration Activate
echo.
echo --- Build method declaration (limit 5) ---
uv run search_code.py -l 5 method declaration "re:^Build$"
echo.
echo --- Abs method in Vector3D (namespace filter) ---
uv run search_code.py -n VRageMath method declaration "re:^Abs$"
echo.

echo ============================================================
echo METHOD USAGE
echo ============================================================
echo --- Activate method usage (limit 5) ---
uv run search_code.py -l 5 method usage Activate
echo.
echo --- ClampToByte method usage (limit 5) ---
uv run search_code.py -l 5 method usage ClampToByte
echo.

echo ============================================================
echo FIELD DECLARATION
echo ============================================================
echo --- AngularDamping field declaration ---
uv run search_code.py field declaration AngularDamping
echo.
echo --- AllowScaling field declaration ---
uv run search_code.py field declaration AllowScaling
echo.
echo --- Forward field declaration (limit 5) ---
uv run search_code.py -l 5 field declaration "re:^Forward$"
echo.

echo ============================================================
echo FIELD USAGE
echo ============================================================
echo --- Forward field usage (limit 5) ---
uv run search_code.py -l 5 field usage "re:^Forward$"
echo.
echo --- AngularDamping field usage (limit 5) ---
uv run search_code.py -l 5 field usage AngularDamping
echo.

echo ============================================================
echo INTERFACE DECLARATION
echo ============================================================
echo --- IMyPhysics interface declaration ---
uv run search_code.py interface declaration IMyPhysics
echo.
echo --- IPhysicsMesh interface declaration ---
uv run search_code.py interface declaration IPhysicsMesh
echo.

echo ============================================================
echo INTERFACE USAGE
echo ============================================================
echo --- IMyEntity interface usage (limit 5) ---
uv run search_code.py -l 5 interface usage IMyEntity
echo.

echo ============================================================
echo ENUM DECLARATION
echo ============================================================
echo --- MyPhysicsOption enum declaration ---
uv run search_code.py enum declaration MyPhysicsOption
echo.
echo --- GridEffectType enum declaration ---
uv run search_code.py enum declaration GridEffectType
echo.

echo ============================================================
echo ENUM USAGE
echo ============================================================
echo --- MyPhysicsOption enum usage (limit 5) ---
uv run search_code.py -l 5 enum usage MyPhysicsOption
echo.

echo ============================================================
echo NAMESPACE FILTERING
echo ============================================================
echo --- Classes in Sandbox.Engine.Physics namespace ---
uv run search_code.py -n Sandbox.Engine.Physics -l 5 class declaration ""
echo.
echo --- Methods in VRageMath namespace containing "Add" ---
uv run search_code.py -n VRageMath -l 5 method declaration Add
echo.

echo ============================================================
echo PAGINATION (LIMIT AND OFFSET)
echo ============================================================
echo --- First 3 Vector3D usages ---
uv run search_code.py -l 3 struct usage Vector3D
echo.
echo --- Next 3 Vector3D usages (offset 3) ---
uv run search_code.py -l 3 -o 3 struct usage Vector3D
echo.
echo --- Skip 6, show 3 ---
uv run search_code.py -l 3 -o 6 struct usage Vector3D
echo.

echo ============================================================
echo COUNT MODE
echo ============================================================
echo --- Count of MyPhysicsBody usages ---
uv run search_code.py -c class usage MyPhysicsBody
echo.
echo --- Count of Vector3D usages ---
uv run search_code.py -c struct usage Vector3D
echo.
echo --- Count of Activate method declarations ---
uv run search_code.py -c method declaration Activate
echo.

echo ============================================================
echo REGEX PATTERNS
echo ============================================================
echo --- Classes starting with "MyPhysics" ---
uv run search_code.py -l 5 class declaration "re:^MyPhysics"
echo.
echo --- Methods ending with "Position" (limit 5) ---
uv run search_code.py -l 5 method declaration "re:Position$"
echo.
echo --- Structs matching "Vector[23]D" ---
uv run search_code.py struct declaration "re:^Vector[23]D$"
echo.

echo ============================================================
echo MULTIPLE PATTERNS (AND logic)
echo ============================================================
echo --- Methods containing both "Get" and "Position" ---
uv run search_code.py -l 5 method declaration Get Position
echo.

echo ============================================================
echo METHOD SIGNATURE SEARCH
echo ============================================================
echo --- Activate method signature ---
uv run search_code.py -l 5 method signature Activate
echo.
echo --- Build method signature (limit 5) ---
uv run search_code.py -l 5 method signature "re:^Build$"
echo.
echo --- Abs method signature in VRageMath namespace ---
uv run search_code.py -n VRageMath method signature "re:^Abs$"
echo.
echo --- Count of GetPosition method signatures ---
uv run search_code.py -c method signature GetPosition
echo.
echo --- Signature containing both "Get" and "Position" ---
uv run search_code.py -l 5 method signature Get Position
echo.

echo ============================================================
echo NON-MATCHING EXAMPLES
echo ============================================================
echo --- Non-existent class ---
uv run search_code.py class declaration ThisClassDoesNotExist12345
echo.
echo --- Non-existent method ---
uv run search_code.py method declaration ZzzNonExistentMethod999
echo.
echo --- Non-matching regex ---
uv run search_code.py struct declaration "re:^ZZZZZ.*XXXXX$"
echo.

echo ============================================================
echo HIERARCHY SEARCH - CLASS PARENT
echo ============================================================
echo --- Find parent of MyGrid ---
uv run search_code.py class parent MyGrid
echo.
echo --- Find parent of MyProjectorBase ---
uv run search_code.py class parent MyProjectorBase
echo.

echo ============================================================
echo HIERARCHY SEARCH - CLASS CHILDREN
echo ============================================================
echo --- Find children of MyEntity (limit 5) ---
uv run search_code.py -l 5 class children MyEntity
echo.
echo --- Find children of MyTerminalBlock (limit 3) ---
uv run search_code.py -l 3 class children MyTerminalBlock
echo.

echo ============================================================
echo HIERARCHY SEARCH - INTERFACE PARENT
echo ============================================================
echo --- Find parent of IMyTerminalBlock ---
uv run search_code.py interface parent IMyTerminalBlock
echo.
echo --- Find parent of IMyFunctionalBlock ---
uv run search_code.py interface parent IMyFunctionalBlock
echo.

echo ============================================================
echo HIERARCHY SEARCH - INTERFACE CHILDREN
echo ============================================================
echo --- Find children of IMyEntity (limit 5) ---
uv run search_code.py -l 5 interface children IMyEntity
echo.
echo --- Find children of IMyCubeBlock (limit 3) ---
uv run search_code.py -l 3 interface children IMyCubeBlock
echo.

echo ============================================================
echo HIERARCHY SEARCH - CLASS IMPLEMENTS
echo ============================================================
echo --- Find interfaces implemented by MyTerminalBlock ---
uv run search_code.py class implements MyTerminalBlock
echo.
echo --- Find interfaces implemented by MyGrid ---
uv run search_code.py class implements MyGrid
echo.

echo ============================================================
echo HIERARCHY SEARCH - INTERFACE IMPLEMENTORS
echo ============================================================
echo --- Find implementors of IMyEntity (limit 5) ---
uv run search_code.py -l 5 interface implementors IMyEntity
echo.
echo --- Find implementors of IMyTerminalBlock (limit 5) ---
uv run search_code.py -l 5 interface implementors IMyTerminalBlock
echo.

echo ============================================================
echo HIERARCHY SEARCH - COUNT MODE
echo ============================================================
echo --- Count children of MyEntity ---
uv run search_code.py -c class children MyEntity
echo.
echo --- Count implementors of IMyEntity ---
uv run search_code.py -c interface implementors IMyEntity
echo.

echo ============================================================
echo HIERARCHY SEARCH - WITH NAMESPACE FILTER
echo ============================================================
echo --- Find children of MyEntity in Sandbox.Game namespace ---
uv run search_code.py -n Sandbox.Game -l 5 class children MyEntity
echo.
echo --- Find implementors of IMyEntity in VRage.Game.ModAPI namespace ---
uv run search_code.py -n VRage.Game.ModAPI -l 3 interface implementors IMyEntity
echo.

echo ============================================================
echo ALL TESTS COMPLETED
echo ============================================================
