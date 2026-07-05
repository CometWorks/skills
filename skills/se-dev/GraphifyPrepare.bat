@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "GRAPHIFY_LABEL=%~1"
set "GRAPHIFY_ROOT=%~2"

REM Graphify is strictly optional and OFF by default. Build only on opt-in.
if not "%SE_DEV_GRAPHIFY%"=="1" (
    echo Graphify: skipping %GRAPHIFY_LABEL% ^(set SE_DEV_GRAPHIFY=1 to build the optional graph^)
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

where graphify >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 call :prompt_install

where graphify >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 exit /b 0

for %%I in ("%GRAPHIFY_ROOT%") do set "GRAPHIFY_ABS_ROOT=%%~fI"
set "GRAPHIFY_OUT=%GRAPHIFY_ABS_ROOT%\graphify-out"

call :check_disk "%GRAPHIFY_ABS_ROOT%"
if %ERRORLEVEL% NEQ 0 (
    echo Graphify: skipping %GRAPHIFY_LABEL% - not enough free disk space. Core prepare already succeeded.
    exit /b 0
)

if not exist "%GRAPHIFY_OUT%\graph.json" goto build

REM graph.json exists; require clustering data or rebuild from scratch.
if not exist "%GRAPHIFY_OUT%\.graphify_analysis.json" (
    echo Graphify: %GRAPHIFY_LABEL% graph is incomplete ^(clustering missing^); rebuilding from scratch
    rmdir /S /Q "%GRAPHIFY_OUT%"
    goto build
)

echo Graphify: updating %GRAPHIFY_LABEL% graph at %GRAPHIFY_ABS_ROOT%
graphify "%GRAPHIFY_ABS_ROOT%" --update
if %ERRORLEVEL% NEQ 0 echo WARNING: Graphify update failed for %GRAPHIFY_LABEL%; prepare continues.
exit /b 0

:build
echo Graphify: building %GRAPHIFY_LABEL% graph at %GRAPHIFY_ABS_ROOT%
graphify "%GRAPHIFY_ABS_ROOT%"
if %ERRORLEVEL% NEQ 0 echo WARNING: Graphify build failed for %GRAPHIFY_LABEL%; prepare continues.
exit /b 0

REM Disk pre-check: the graph output (graph.json + clustering + cache) runs ~9x
REM the corpus size, so require 12x the corpus plus 1 GiB headroom. Returns
REM errorlevel 1 when there is not enough free space on the graph volume.
:check_disk
powershell -NoProfile -ExecutionPolicy Bypass -Command "$root=[IO.Path]::GetFullPath('%~1'); $out=Join-Path $root 'graphify-out'; $total=(Get-ChildItem -LiteralPath $root -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum; $og=0; if (Test-Path -LiteralPath $out) { $og=(Get-ChildItem -LiteralPath $out -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum }; $corpusMB=[math]::Floor(($total-$og)/1MB); $needMB=$corpusMB*12+1024; $freeMB=[math]::Floor((Get-Item -LiteralPath $root).PSDrive.Free/1MB); if ($freeMB -lt $needMB) { Write-Host ('  Needed (graph + cache + 1 GiB headroom): ~'+$needMB+' MB'); Write-Host ('  Available on the graph volume:           ~'+$freeMB+' MB'); exit 1 } else { Write-Host ('Graphify: disk pre-check OK (need ~'+$needMB+' MB, have ~'+$freeMB+' MB)'); exit 0 }"
exit /b %ERRORLEVEL%

:prompt_install
echo Graphify builds a navigable map beside the regular search indexes. >CON
echo Install options: >CON
echo   uv tool install graphifyy >CON
echo   pipx install graphifyy >CON
echo   pip install graphifyy >CON
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
    uv tool install graphifyy
    goto after_package_install
)

where pipx >NUL 2>NUL
if %ERRORLEVEL% EQU 0 (
    pipx install graphifyy
    goto after_package_install
)

python -m pip install graphifyy

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
