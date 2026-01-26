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
echo VARIABLE DECLARATION
echo ============================================================
echo --- AngularDamping variable declaration ---
uv run search_code.py variable declaration AngularDamping
echo.
echo --- AllowScaling variable declaration ---
uv run search_code.py variable declaration AllowScaling
echo.
echo --- Forward variable declaration (limit 5) ---
uv run search_code.py -l 5 variable declaration "re:^Forward$"
echo.

echo ============================================================
echo VARIABLE USAGE
echo ============================================================
echo --- Forward variable usage (limit 5) ---
uv run search_code.py -l 5 variable usage "re:^Forward$"
echo.
echo --- AngularDamping variable usage (limit 5) ---
uv run search_code.py -l 5 variable usage AngularDamping
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
echo --- IMyPhysics interface usage (limit 5) ---
uv run search_code.py -l 5 interface usage IMyPhysics
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
echo ALL TESTS COMPLETED
echo ============================================================
