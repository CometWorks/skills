@echo off

:: 1. Detect game install location (env var override takes precedence)
if defined SE_GAME_ROOT goto have_game_root

:: Try the game's registry key
for /f "tokens=2*" %%A in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244850" /v "InstallLocation" 2^>nul') do (
    set "SE_GAME_ROOT=%%B"
)

if defined SE_GAME_ROOT goto have_game_root
echo ERROR: Could not detect Space Engineers install location.
echo Please set the SE_GAME_ROOT environment variable to the game's root folder
echo (the folder containing Bin64, Content, etc.)
goto failed

:have_game_root
echo Game Root: %SE_GAME_ROOT%

:: 2. Derive workshop path from game install location
for %%I in ("%SE_GAME_ROOT%\..\..") do set "STEAMAPPS_PATH=%%~fI"
set "WORKSHOP_PATH=%STEAMAPPS_PATH%\workshop\content\244850"
echo Workshop Path: %WORKSHOP_PATH%

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

if exist SteamScripts goto skip_steam_scripts
echo Linking the Steam content folder as SteamScripts
mklink /J SteamScripts "%WORKSHOP_PATH%"
if %ERRORLEVEL% EQU 0 goto skip_steam_scripts
echo ERROR: Missing Steam content folder
echo Please fix the folder path on the `mklink` line in the `Prepare.bat` script.
goto failed
:skip_steam_scripts

if exist LocalScripts goto skip_local_scripts
echo Linking the game's local IngameScript\local folder as LocalScripts
mklink /J LocalScripts "%AppData%\SpaceEngineers\IngameScripts\local"
if %ERRORLEVEL% EQU 0 goto skip_local_scripts
echo ERROR: Missing local IngameScripts\local folder, this should not happen
goto failed
:skip_local_scripts

echo Indexing script code (this may take a while)
uv run index_scripts.py
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
