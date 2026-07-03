@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "GRAPHIFY_LABEL=%~1"
set "GRAPHIFY_ROOT=%~2"

if /I "%SE_DEV_GRAPHIFY%"=="0" (
    echo Graphify disabled by SE_DEV_GRAPHIFY=0
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

if exist "%GRAPHIFY_ABS_ROOT%\graphify-out\graph.json" (
    echo Graphify: updating %GRAPHIFY_LABEL% graph at %GRAPHIFY_ABS_ROOT%
    graphify "%GRAPHIFY_ABS_ROOT%" --update
) else (
    echo Graphify: building %GRAPHIFY_LABEL% graph at %GRAPHIFY_ABS_ROOT%
    graphify "%GRAPHIFY_ABS_ROOT%"
)

if %ERRORLEVEL% NEQ 0 echo WARNING: Graphify failed for %GRAPHIFY_LABEL%; prepare continues.
exit /b 0

:prompt_install
echo Graphify is highly recommended for navigable maps of prepared se-dev corpora. >CON
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
