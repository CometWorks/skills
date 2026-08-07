@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Graphify query smoke test for the decompiled game-code graph (Windows).
REM Mirrors test_search_game_code.bat but exercises the optional Graphify graph.
REM The asserted checks live in test_graphify_queries.py, shared with the Linux
REM wrapper. Exits non-zero if any check failed.

set "GRAPH_ROOT=%SE_DEV_GAME_CODE_GRAPH_ROOT%"
if "%GRAPH_ROOT%"=="" set "GRAPH_ROOT=Data\Decompiled"
REM graphify-out sits beside Decompiled, not inside it.
set "GRAPH_OUT=%SE_DEV_GAME_CODE_GRAPH_OUT%"
if "%GRAPH_OUT%"=="" set "GRAPH_OUT=Data"
if "%GRAPHIFY_MAX_GRAPH_BYTES%"=="" set "GRAPHIFY_MAX_GRAPH_BYTES=2GB"

echo ============================================================
echo GRAPHIFY HEALTH CHECK
echo ============================================================
where graphify >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo SKIP: graphify is not on PATH. Build the graph by running prepare:
    echo   .\Prepare.bat   REM auto-builds with the fast Rust backend; set SE_DEV_GRAPHIFY=1 to force the slow fallback
    exit /b 1
)
call "%~dp0..\se-dev\GraphifyCheck.bat" "%GRAPH_OUT%"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FAIL: Graphify graph is missing or unusable. Rebuild it by re-running prepare:
    echo   rmdir /S /Q "%GRAPH_OUT%\graphify-out"
    echo   .\Prepare.bat   REM auto-builds with the fast Rust backend; set SE_DEV_GRAPHIFY=1 to force the slow fallback
    exit /b 1
)
echo.

uv run test_graphify_queries.py "%GRAPH_OUT%"
exit /b %ERRORLEVEL%
