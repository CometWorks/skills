@echo off

:: 1. Get the Steam Install Path from the Registry
for /f "tokens=2*" %%A in ('reg query "HKEY_CURRENT_USER\Software\Valve\Steam" /v "SteamPath" 2^>nul') do (
    set "STEAM_ROOT=%%B"
)

:: 2. Clean up the path (Registry uses forward slashes, Batch prefers backslashes)
set "STEAM_ROOT=%STEAM_ROOT:/=\%"

:: 3. Define your target folders
set "WORKSHOP_PATH=%STEAM_ROOT%\steamapps\workshop\content"
set "COMMON_PATH=%STEAM_ROOT%\steamapps\common"

:: Output results to verify
echo Steam Root:    %STEAM_ROOT%
echo Workshop Path: %WORKSHOP_PATH%
echo Common Path:   %COMMON_PATH%

echo Verifying Python
python --version
if %ERRORLEVEL% EQU 0 goto has_python
echo ERROR: Missing Python
echo Please install Python 3.13 or newer. 
echo Make sure python.exe is on PATH.
goto failed
:has_python

uv -V 2>NUL
if %ERRORLEVEL% EQU 0 goto skip_uv
echo Installing uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv -V
if %ERRORLEVEL% NEQ 0 goto failed
:skip_uv

if exist .venv goto skip_venv
echo Setting up Python .venv (uv sync)
uv sync
:skip_venv

if exist busybox.exe goto skip_busybox
echo Downloading busybox
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://frippery.org/files/busybox/busybox64u.exe -OutFile busybox.exe"
if %ERRORLEVEL% NEQ 0 goto failed
:skip_busybox

if exist SteamMods goto skip_steam_mods
echo Linking the Steam content folder as SteamMods
mklink /J SteamMods "%WORKSHOP_PATH%\244850"
if %ERRORLEVEL% EQU 0 goto skip_steam_mods
echo ERROR: Missing Steam content folder
echo Please fix the folder path on the `mklink` line in the `Prepare.bat` script.
goto failed
:skip_steam_mods

if exist LocalMods goto skip_local_mods
echo Linking the game's local Mods folder as LocalMods
mklink /J LocalMods "%AppData%\SpaceEngineers\Mods"
if %ERRORLEVEL% EQU 0 goto skip_local_mods
echo ERROR: Missing local Mods folder, this should not happen
goto failed
:skip_local_mods

echo Indexing mod code (this may take a while)
uv run index_mods.py
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
