@echo off
REM DetectGameRoot.bat - detect the Space Engineers install root (the folder
REM holding Bin64, Content, etc.) and leave it in the caller's SE_GAME_ROOT
REM variable. Invoke it with `call`; it deliberately does NOT use setlocal,
REM otherwise the variable would not survive the return.
REM
REM Windows counterpart of detect_game_root() in common-posix.sh. An already
REM defined SE_GAME_ROOT always wins, so a custom install location can be
REM pointed at manually. Exits with 1 when the install cannot be located.

if defined SE_GAME_ROOT exit /b 0

REM The game's Steam uninstall key records the install location.
for /f "tokens=2*" %%A in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244850" /v "InstallLocation" 2^>nul') do (
    set "SE_GAME_ROOT=%%B"
)

if defined SE_GAME_ROOT exit /b 0

echo ERROR: Could not detect Space Engineers install location.
echo Please set the SE_GAME_ROOT environment variable to the game's root folder
echo (the folder containing Bin64, Content, etc.)
exit /b 1
