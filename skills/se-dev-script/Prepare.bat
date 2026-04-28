@echo off
setlocal EnableDelayedExpansion

:: 1. Verify Python is available
echo Verifying Python
python --version
if %ERRORLEVEL% EQU 0 goto has_python
echo ERROR: Missing Python
echo Please install Python 3.13 or newer.
echo Make sure python.exe is on PATH.
goto failed
:has_python

:: 2. Install uv if missing
uv -V 2>NUL
if %ERRORLEVEL% EQU 0 goto skip_uv
echo Installing uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv -V
if %ERRORLEVEL% NEQ 0 goto failed
:skip_uv

:: 3. Set up Python venv
if exist .venv goto skip_venv
echo Setting up Python .venv (uv sync)
uv sync
:skip_venv

:: 4. Download busybox if missing
if exist busybox.exe goto skip_busybox
echo Downloading busybox
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://frippery.org/files/busybox/busybox64u.exe -OutFile busybox.exe"
if %ERRORLEVEL% NEQ 0 goto failed
:skip_busybox

:: 5. Set up the Data folder under %USERPROFILE% and create a Data junction.
:: See se-dev-game-code/Prepare.bat for why %USERPROFILE% is used over %LOCALAPPDATA%.
set "DATA_ROOT=%USERPROFILE%\.se-dev\script"
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

:: 6. Link the game's local IngameScripts/local folder as LocalScripts
if exist LocalScripts goto skip_local_scripts
echo Linking the game's local IngameScripts\local folder as LocalScripts
mklink /J LocalScripts "%AppData%\SpaceEngineers\IngameScripts\local"
if %ERRORLEVEL% EQU 0 goto skip_local_scripts
echo ERROR: Missing local IngameScripts\local folder, this should not happen
goto failed
:skip_local_scripts

:: 7. Build the quick script inventory (cheap; safe to rerun before tasks)
echo Building script inventory
uv run python -u list_scripts.py
if %ERRORLEVEL% NEQ 0 goto failed

:: 8. Build (or incrementally update) the full code index
echo Indexing script code (incremental: only changed scripts are reparsed)
uv run python -u index_scripts.py
if %ERRORLEVEL% NEQ 0 goto failed

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
