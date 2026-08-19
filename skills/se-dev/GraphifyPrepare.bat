@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Usage: GraphifyPrepare.bat <label> <root> [out-dir] [source-state]
REM   <root>          the tree to graph
REM   <out-dir>       where to put graphify-out\ (default: <root>). Pass a directory
REM                   outside <root> to keep the graphed tree free of build output.
REM   <source-state>  "unchanged" when the caller knows nothing under <root> was
REM                   regenerated in this run, so an existing healthy graph still
REM                   matches its sources and is left untouched. Anything else
REM                   (default "changed") builds or updates as before.
set "GRAPHIFY_LABEL=%~1"
set "GRAPHIFY_ROOT=%~2"
set "GRAPHIFY_OUT_DIR=%~3"
set "GRAPHIFY_SOURCE_STATE=%~4"
if "%GRAPHIFY_OUT_DIR%"=="" set "GRAPHIFY_OUT_DIR=%GRAPHIFY_ROOT%"
if "%GRAPHIFY_SOURCE_STATE%"=="" set "GRAPHIFY_SOURCE_STATE=changed"

REM Clustering is the slow part of a Graphify build. The fast path is graspologic's
REM native Rust Leiden backend (needs Python 3.12); without it Graphify drops to a
REM single-core Python fallback (~10-30 min for game/server code). We default the
REM Graphify tool to Python 3.12 with the leiden extra. When the fast backend is
REM available the graph is built automatically; otherwise it stays optional and only
REM builds on opt-in (SE_DEV_GRAPHIFY=1). SE_DEV_GRAPHIFY=0 disables it entirely.
set "GRAPHIFY_PY_VER=3.12"

REM The decompiled game/server-code graph.json is well over Graphify's default 512 MB
REM load cap, which would abort every build and update. Raise it, but let an explicitly
REM set value win so a larger corpus can be accommodated without editing this file.
if "%GRAPHIFY_MAX_GRAPH_BYTES%"=="" set "GRAPHIFY_MAX_GRAPH_BYTES=2GB"

if "%SE_DEV_GRAPHIFY%"=="0" (
    echo Graphify: skipping %GRAPHIFY_LABEL% ^(SE_DEV_GRAPHIFY=0^)
    exit /b 0
)

if "%GRAPHIFY_ROOT%"=="" (
    echo Graphify: skipping %GRAPHIFY_LABEL% ^(empty root^)
    exit /b 0
)

if not exist "%GRAPHIFY_ROOT%\" (
    echo Graphify: skipping %GRAPHIFY_LABEL% ^(missing root: %GRAPHIFY_ROOT%^)
    exit /b 0
)

REM Sources unchanged and the existing graph is usable: there is nothing to do.
REM Checked before provisioning so an up-to-date graph costs neither a tool
REM install nor the disk pre-check scan of the whole corpus.
if /I "%GRAPHIFY_SOURCE_STATE%"=="unchanged" (
    call :graph_status "%GRAPHIFY_OUT_DIR%"
    if !ERRORLEVEL! EQU 0 (
        echo Graphify: %GRAPHIFY_LABEL% graph is up to date ^(sources unchanged^); skipping
        exit /b 0
    )
)

REM Provision/detect the fast Rust Leiden backend. Positive confirmation only:
REM any uncertainty leaves GRAPHIFY_FAST unset and we fall back to opt-in.
call :detect_fast

if "%GRAPHIFY_FAST%"=="1" (
    where graphify >NUL 2>NUL
    if !ERRORLEVEL! EQU 0 (
        echo Graphify: fast native Rust Leiden backend active - building %GRAPHIFY_LABEL% automatically.
        goto have_graphify
    )
    echo WARNING: fast Rust backend detected but graphify is not on PATH; skipping graph build.
    exit /b 0
)

REM Slow single-core fallback: keep Graphify optional unless the user opted in.
if not "%SE_DEV_GRAPHIFY%"=="1" (
    echo Graphify: skipping %GRAPHIFY_LABEL% - fast Rust clustering backend unavailable ^(needs uv + Python %GRAPHIFY_PY_VER%^).
    echo   Building now would use the slow single-core fallback ^(~10-30 min for game/server code^). Set SE_DEV_GRAPHIFY=1 to build anyway.
    exit /b 0
)
echo Graphify: fast Rust backend unavailable; building %GRAPHIFY_LABEL% with the slow single-core fallback ^(expect ~10-30 min for game/server code^).

where graphify >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 call :prompt_install

where graphify >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 exit /b 0

:have_graphify
for %%I in ("%GRAPHIFY_ROOT%") do set "GRAPHIFY_ABS_ROOT=%%~fI"
if not exist "%GRAPHIFY_OUT_DIR%\" mkdir "%GRAPHIFY_OUT_DIR%" 2>NUL
for %%I in ("%GRAPHIFY_OUT_DIR%") do set "GRAPHIFY_ABS_OUT_DIR=%%~fI"
set "GRAPHIFY_OUT=%GRAPHIFY_ABS_OUT_DIR%\graphify-out"

call :check_disk "%GRAPHIFY_ABS_ROOT%"
if %ERRORLEVEL% NEQ 0 (
    echo Graphify: skipping %GRAPHIFY_LABEL% - not enough free disk space. Core prepare already succeeded.
    exit /b 0
)

call :graph_status "%GRAPHIFY_ABS_OUT_DIR%"
if %ERRORLEVEL% EQU 2 goto build
if %ERRORLEVEL% EQU 3 (
    echo Graphify: %GRAPHIFY_LABEL% graph is incomplete ^(clustering missing or interrupted^); rebuilding from scratch
    rmdir /S /Q "%GRAPHIFY_OUT%"
    goto build
)

echo Graphify: updating %GRAPHIFY_LABEL% graph of %GRAPHIFY_ABS_ROOT% at %GRAPHIFY_OUT%
REM --out is passed only when it differs from the root, so the default
REM invocation stays identical to what the other skills have always run.
if /I "%GRAPHIFY_ABS_OUT_DIR%"=="%GRAPHIFY_ABS_ROOT%" (
    graphify "%GRAPHIFY_ABS_ROOT%" --update
) else (
    graphify "%GRAPHIFY_ABS_ROOT%" --update --out "%GRAPHIFY_ABS_OUT_DIR%"
)
if %ERRORLEVEL% NEQ 0 echo WARNING: Graphify update failed for %GRAPHIFY_LABEL%; prepare continues.
exit /b 0

:build
echo Graphify: building %GRAPHIFY_LABEL% graph of %GRAPHIFY_ABS_ROOT% at %GRAPHIFY_OUT%
if /I "%GRAPHIFY_ABS_OUT_DIR%"=="%GRAPHIFY_ABS_ROOT%" (
    graphify "%GRAPHIFY_ABS_ROOT%"
) else (
    graphify "%GRAPHIFY_ABS_ROOT%" --out "%GRAPHIFY_ABS_OUT_DIR%"
)
if %ERRORLEVEL% NEQ 0 echo WARNING: Graphify build failed for %GRAPHIFY_LABEL%; prepare continues.
exit /b 0

REM Make the fast Rust Leiden backend available and confirm it. Sets GRAPHIFY_FAST=1
REM only on positive confirmation (graspologic imports in the Graphify tool venv).
REM Any failure is left as "not fast" so behaviour degrades to the opt-in fallback.
:detect_fast
set "GRAPHIFY_FAST="
where uv >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 goto detect_fast_done

REM Put uv's tool bin dir on PATH so a freshly-installed graphify is callable here.
for /f "usebackq delims=" %%B in (`uv tool dir --bin 2^>NUL`) do set "PATH=%%B;%PATH%"

call :fast_probe
if "%GRAPHIFY_FAST%"=="1" goto detect_fast_done

echo Graphify: provisioning the fast Rust clustering backend ^(uv + Python %GRAPHIFY_PY_VER%; one-time ~30-60s^)...
uv tool install --python %GRAPHIFY_PY_VER% --force "graphifyy[leiden]" >NUL 2>NUL
if defined SE_DEV_GRAPHIFY_PLATFORM graphify install --platform "%SE_DEV_GRAPHIFY_PLATFORM%" >NUL 2>NUL
call :fast_probe
:detect_fast_done
exit /b 0

REM Probe the uv tool venv for a working graspologic (Rust Leiden). Sets GRAPHIFY_FAST=1 on success.
:fast_probe
set "GRAPHIFY_FAST="
set "UVTOOLS="
for /f "usebackq delims=" %%D in (`uv tool dir 2^>NUL`) do set "UVTOOLS=%%D"
if not defined UVTOOLS exit /b 0
set "GRAPHIFY_TOOL_PY=%UVTOOLS%\graphifyy\Scripts\python.exe"
if not exist "%GRAPHIFY_TOOL_PY%" exit /b 0
"%GRAPHIFY_TOOL_PY%" -c "import graspologic.partition" >NUL 2>NUL
if %ERRORLEVEL% EQU 0 set "GRAPHIFY_FAST=1"
exit /b 0

REM Classify the graph under <out-dir>\graphify-out. Mirrors se_dev_graphify_status
REM in graphify-prepare.sh and the exit codes of GraphifyCheck.bat:
REM   0 ok, 2 missing (never built), 3 incomplete (build or clustering interrupted).
:graph_status
set "GS_OUT=%~f1\graphify-out"
if not exist "%GS_OUT%\graph.json" exit /b 2
REM A truncated or empty graph.json means the build died mid-write.
for %%F in ("%GS_OUT%\graph.json") do if %%~zF LSS 1024 exit /b 3
REM Clustering writes .graphify_analysis.json. Without it every node has an empty
REM community and the graph is only half-built.
if not exist "%GS_OUT%\.graphify_analysis.json" exit /b 3
exit /b 0

REM Disk pre-check: the graph output (graph.json + clustering + cache) runs ~9x
REM the corpus size, so require 12x the corpus plus 1 GiB headroom. Returns
REM errorlevel 1 when there is not enough free space on the graph volume.
:check_disk
powershell -NoProfile -ExecutionPolicy Bypass -Command "$root=[IO.Path]::GetFullPath('%~1'); $out=Join-Path $root 'graphify-out'; $total=(Get-ChildItem -LiteralPath $root -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum; $og=0; if (Test-Path -LiteralPath $out) { $og=(Get-ChildItem -LiteralPath $out -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum }; $corpusMB=[math]::Floor(($total-$og)/1MB); $needMB=$corpusMB*12+1024; $freeMB=[math]::Floor((Get-Item -LiteralPath $root).PSDrive.Free/1MB); if ($freeMB -lt $needMB) { Write-Host ('  Needed (graph + cache + 1 GiB headroom): ~'+$needMB+' MB'); Write-Host ('  Available on the graph volume:           ~'+$freeMB+' MB'); exit 1 } else { Write-Host ('Graphify: disk pre-check OK (need ~'+$needMB+' MB, have ~'+$freeMB+' MB)'); exit 0 }"
exit /b %ERRORLEVEL%

:prompt_install
echo Graphify builds a navigable map beside the regular search indexes. >CON
echo Fast clustering needs the native Rust Leiden backend ^(graspologic on Python %GRAPHIFY_PY_VER%^). >CON
echo Install options: >CON
echo   uv tool install --python %GRAPHIFY_PY_VER% "graphifyy[leiden]"   ^(recommended: fast backend^) >CON
echo   pipx install "graphifyy[leiden]" >CON
echo   pip install "graphifyy[leiden]" >CON
echo Then wire it into your AI platform: >CON
echo   graphify install --platform [AI PLATFORM] >CON
set "GRAPHIFY_INSTALL="
set /P "GRAPHIFY_INSTALL=Install Graphify now? [y/N] " <CON >CON
if /I not "%GRAPHIFY_INSTALL%"=="y" if /I not "%GRAPHIFY_INSTALL%"=="yes" (
    echo Graphify install declined; skipping graph build.
    exit /b 1
)

where uv >NUL 2>NUL
if %ERRORLEVEL% EQU 0 (
    uv tool install --python %GRAPHIFY_PY_VER% --force "graphifyy[leiden]"
    goto after_package_install
)

where pipx >NUL 2>NUL
if %ERRORLEVEL% EQU 0 (
    pipx install "graphifyy[leiden]"
    goto after_package_install
)

python -m pip install "graphifyy[leiden]"

:after_package_install
where graphify >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Graphify install completed but graphify is still not on PATH; skipping graph build.
    exit /b 1
)

if defined SE_DEV_GRAPHIFY_PLATFORM (
    graphify install --platform "%SE_DEV_GRAPHIFY_PLATFORM%"
    if %ERRORLEVEL% NEQ 0 echo WARNING: graphify platform install failed for "%SE_DEV_GRAPHIFY_PLATFORM%".
    exit /b 0
)

set "GRAPHIFY_PLATFORM="
set /P "GRAPHIFY_PLATFORM=Enter Graphify AI platform for graphify install --platform, or press Enter to skip: " <CON >CON
if not "%GRAPHIFY_PLATFORM%"=="" (
    graphify install --platform "%GRAPHIFY_PLATFORM%"
    if %ERRORLEVEL% NEQ 0 echo WARNING: graphify platform install failed for "%GRAPHIFY_PLATFORM%".
) else (
    echo Graphify package installed. To wire it into your AI platform later, run:
    echo   graphify install --platform [AI PLATFORM]
)
exit /b 0
