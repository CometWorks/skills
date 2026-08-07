@echo off
setlocal EnableDelayedExpansion

REM 1. Verify Python is available
echo Verifying Python
python --version
if %ERRORLEVEL% EQU 0 goto has_python
echo ERROR: Missing Python
echo Please install Python 3.11 or newer.
echo Make sure python.exe is on PATH.
goto failed
:has_python

REM 2. Install uv if missing
uv -V 2>NUL
if %ERRORLEVEL% EQU 0 goto skip_uv
echo Installing uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv -V
if %ERRORLEVEL% NEQ 0 goto failed
:skip_uv

REM 3. Set up Python venv
if exist .venv goto skip_venv
echo Setting up Python .venv (uv sync)
uv sync
:skip_venv

REM 4. Download busybox if missing
if exist busybox.exe goto skip_busybox
echo Downloading busybox
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://frippery.org/files/busybox/busybox64u.exe -OutFile busybox.exe"
if %ERRORLEVEL% NEQ 0 goto failed
:skip_busybox

REM 5. Set up the Data folder under %USERPROFILE% and create a Data junction.
REM See se-dev-game-code/Prepare.bat for why %USERPROFILE% is used over %LOCALAPPDATA%.
set "DATA_ROOT=%USERPROFILE%\.se-dev\mod"
echo Data Root: %DATA_ROOT%
if not exist "%DATA_ROOT%" (
    echo Creating Data Root folder
    mkdir "%DATA_ROOT%"
    if !ERRORLEVEL! NEQ 0 goto failed
)

if exist Data goto skip_data_junction
echo Linking the Data folder
mklink /J Data "%DATA_ROOT%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not create Data junction.
    goto failed
)
:skip_data_junction

REM 6. Link the game's local Mods folder as LocalMods (user development mods)
set "LOCAL_MODS_TARGET=%AppData%\SpaceEngineers\Mods"
if exist LocalMods goto skip_local_mods
echo Linking the game's local Mods folder as LocalMods
mklink /J LocalMods "%LOCAL_MODS_TARGET%"
if %ERRORLEVEL% EQU 0 goto skip_local_mods
echo ERROR: Missing local Mods folder, this should not happen
goto failed
:skip_local_mods

REM 7. Build the quick mod inventory (cheap; safe to rerun before tasks)
echo Building mod inventory
uv run python -u list_mods.py
if %ERRORLEVEL% NEQ 0 goto failed

REM 8. Build (or incrementally update) the full code index
echo Indexing mod code (incremental: only changed mods are reparsed)
uv run python -u index_mods.py
if %ERRORLEVEL% NEQ 0 goto failed

if defined SE_DEV_MOD_PROJECT_ROOT (
    set "MOD_GRAPH_ROOT=%SE_DEV_MOD_PROJECT_ROOT%"
) else (
    set "MOD_GRAPH_ROOT=%LOCAL_MODS_TARGET%"
)
call "%~dp0..\se-dev\GraphifyPrepare.bat" "se-dev-mod" "%MOD_GRAPH_ROOT%"

echo DONE
del "\\?\%cd%\nul" 2>error.txt
del error.txt
echo DONE >Prepare.DONE
exit /b 0

:failed
del "\\?\%cd%\nul" 2>error.txt
del error.txt
echo FAILED
exit /b 1
