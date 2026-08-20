@echo off
REM DetectServerRoot.bat - detect the Space Engineers Dedicated Server install
REM root (the folder holding DedicatedServer64, Content, etc.) and leave it in
REM the caller's SE_SERVER_ROOT variable. Invoke it with `call`; it deliberately
REM does NOT use setlocal, otherwise the variable would not survive the return.
REM
REM Windows counterpart of detect_server_root() in common-posix.sh. An already
REM defined SE_SERVER_ROOT always wins, so a custom install location can be
REM pointed at manually. Exits with 1 when the install cannot be located.

if defined SE_SERVER_ROOT exit /b 0

REM The game's Steam uninstall key records the game install location; the server
REM sits next to it in the same steamapps folder, under the same name plus the
REM DedicatedServer suffix (...\common\SpaceEngineersDedicatedServer).
for /f "tokens=2*" %%A in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244850" /v "InstallLocation" 2^>nul') do (
    set "SE_SERVER_ROOT=%%BDedicatedServer"
)

if defined SE_SERVER_ROOT exit /b 0

echo ERROR: Could not detect Space Engineers Dedicated Server install location.
echo Please set the SE_SERVER_ROOT environment variable to the server's root folder
echo (the folder containing DedicatedServer64, Content, etc.)
exit /b 1
