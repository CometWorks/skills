@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Standalone Graphify health check (Windows).
REM
REM Usage: GraphifyCheck.bat [graph-root]
REM   graph-root  Directory containing graphify-out\ (default: Data\Decompiled)
REM
REM Exit codes: 0 ok, 2 missing, 3 incomplete.
REM A non-zero result means the graph is unusable and must be rebuilt from
REM scratch. Rebuild is expensive for game/server code (~10-30 min); confirm
REM with the user before doing it.

set "ROOT=%~1"
if "%ROOT%"=="" set "ROOT=Data\Decompiled"

if not exist "%ROOT%\" (
    echo FAIL: graph root does not exist: %ROOT%
    echo Run prepare first ^(with SE_DEV_GRAPHIFY=1 to build the optional graph^).
    exit /b 2
)

for %%I in ("%ROOT%") do set "ABS_ROOT=%%~fI"
set "OUT=%ABS_ROOT%\graphify-out"

if not exist "%OUT%\graph.json" (
    echo MISSING: no Graphify graph at %OUT%
    echo Build it with: set SE_DEV_GRAPHIFY=1 ^&^& ^<prepare script^>
    exit /b 2
)

if not exist "%OUT%\.graphify_analysis.json" (
    echo INCOMPLETE: %OUT% has a graph.json but clustering data is missing.
    echo The graph is unusable and must be rebuilt from scratch.
    echo Clean and rebuild ^(this can take ~10-30 min for game/server code^):
    echo   rmdir /S /Q "%OUT%"
    echo   set SE_DEV_GRAPHIFY=1 ^&^& ^<prepare script^>
    exit /b 3
)

echo OK: graph.json and clustering data present at %OUT%
exit /b 0
