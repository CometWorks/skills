@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Graphify query smoke test for the decompiled dedicated-server graph.
REM Mirrors test_search_server_code.bat but exercises the optional Graphify graph.

set "GRAPH_ROOT=%SE_DEV_SERVER_CODE_GRAPH_ROOT%"
if "%GRAPH_ROOT%"=="" set "GRAPH_ROOT=Data\Decompiled"
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
call "%~dp0..\se-dev\GraphifyCheck.bat" "%GRAPH_ROOT%"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo FAIL: Graphify graph is missing or unusable. Rebuild it by re-running prepare:
    echo   rmdir /S /Q "%GRAPH_ROOT%\graphify-out"
    echo   .\Prepare.bat   REM auto-builds with the fast Rust backend; set SE_DEV_GRAPHIFY=1 to force the slow fallback
    exit /b 1
)
echo.

pushd "%GRAPH_ROOT%"

echo ============================================================
echo QUERY - BFS traversal for a question
echo ============================================================
echo --- How does the dedicated server start a session? ---
graphify query "How does the dedicated server start a session?" --budget 400
echo.
echo --- How does the server handle multiplayer clients? ---
graphify query "How does the server handle multiplayer clients?" --budget 400
echo.

echo ============================================================
echo QUERY - narrowed by edge context
echo ============================================================
echo --- Call edges out of MyCubeGrid ---
graphify query "MyCubeGrid" --context call --budget 300
echo.

echo ============================================================
echo EXPLAIN - a node and its neighbours
echo ============================================================
echo --- Explain MySession ---
graphify explain "MySession"
echo.
echo --- Explain MyEntity ---
graphify explain "MyEntity"
echo.

echo ============================================================
echo PATH - shortest path between two nodes
echo ============================================================
echo --- MyCubeBlock -^> MyEntity ---
graphify path "MyCubeBlock" "MyEntity"
echo.

echo ============================================================
echo AFFECTED - reverse traversal for impact
echo ============================================================
echo --- What is affected by MyEntity? ---
graphify affected "MyEntity" --depth 1
echo.

popd

echo ============================================================
echo ALL TESTS COMPLETED
echo ============================================================
