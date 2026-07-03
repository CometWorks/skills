@echo off
setlocal EnableDelayedExpansion

:: 1. Detect server install location (env var override takes precedence)
if defined SE_SERVER_ROOT goto have_server_root

:: Try the game's registry key, then append DedicatedServer to derive the server path
for /f "tokens=2*" %%A in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 244850" /v "InstallLocation" 2^>nul') do (
    set "SE_SERVER_ROOT=%%BDedicatedServer"
)

if defined SE_SERVER_ROOT goto have_server_root
echo ERROR: Could not detect Space Engineers Dedicated Server install location.
echo Please set the SE_SERVER_ROOT environment variable to the server's root folder
echo (the folder containing DedicatedServer64, Content, etc.)
goto failed

:have_server_root
echo Server Root: %SE_SERVER_ROOT%

:: 2. Verify Python is available
echo Verifying Python
python --version
if %ERRORLEVEL% EQU 0 goto has_python
echo ERROR: Missing Python
echo Please install Python 3.11 or newer.
echo Make sure python.exe is on PATH.
goto failed
:has_python

:: 3. Verify command line git is available
echo Verifying git
git --version
if %ERRORLEVEL% EQU 0 goto has_git
echo ERROR: Missing git
echo Please install git for Windows from https://git-scm.com/download/win
echo Make sure git.exe is on PATH.
goto failed
:has_git

:: 4. Install uv if missing
uv -V 2>NUL
if %ERRORLEVEL% EQU 0 goto skip_uv
echo Installing uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv -V
if %ERRORLEVEL% NEQ 0 goto failed
:skip_uv

:: 5. Set up Python venv
if exist .venv goto skip_venv
echo Setting up Python .venv (uv sync)
uv sync
:skip_venv

:: 6. Download busybox if missing
if exist busybox.exe goto skip_busybox
echo Downloading busybox
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://frippery.org/files/busybox/busybox64u.exe -OutFile busybox.exe"
if %ERRORLEVEL% NEQ 0 goto failed
:skip_busybox

:: 7. Install ILSpy if missing
set ILSPY_VERSION=10.0.1.8346
for /f "delims=" %%V in ('ilspycmd -v 2^>NUL') do set ILSPY_INSTALLED=%%V
if defined ILSPY_INSTALLED (
    echo ilspycmd version %ILSPY_INSTALLED% has already been installed
    goto skip_ilspycmd
)
echo Installing ilspycmd %ILSPY_VERSION%
dotnet tool install --global ilspycmd --version %ILSPY_VERSION%
if %ERRORLEVEL% NEQ 0 goto failed
ilspycmd -v
if %ERRORLEVEL% NEQ 0 goto failed
:skip_ilspycmd

:: 8. Set up the Data folder under %USERPROFILE% and create a Data junction.
:: Using %USERPROFILE% rather than %LOCALAPPDATA% keeps the data outside the
:: UWP filesystem virtualization layer (Claude Code is a packaged app whose
:: writes under %LOCALAPPDATA% would be silently redirected into its
:: per-package LocalCache, hiding the data from regular tools).
set "DATA_ROOT=%USERPROFILE%\.se-dev\server-code"
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

:: 9. Initialize a local Git repository in the Data folder if missing
if exist Data\.git goto skip_git_init
echo Initializing local Git repository in the Data folder
pushd Data
git init
if %ERRORLEVEL% NEQ 0 (
    popd
    goto failed
)
:: Ensure default branch is main
git symbolic-ref HEAD refs/heads/main 2>NUL

:: Required: some decompiled paths exceed the legacy MAX_PATH (260 chars),
:: e.g. EmptyKeys generated bindings under SpaceEngineers.Game.
git config core.longpaths true

:: Write .gitignore
> .gitignore (
    echo CodeIndex/
    echo Content/
    echo __pycache__/
    echo *.py[cod]
    echo *.bak
    echo *.log
)

git add .gitignore
if %ERRORLEVEL% NEQ 0 (
    popd
    goto failed
)
git -c user.name="se-dev-skills" -c user.email="se-dev-skills@localhost" commit -m "Initial commit: .gitignore"
if %ERRORLEVEL% NEQ 0 (
    popd
    goto failed
)
popd
:skip_git_init

:: 10. Link the server's DedicatedServer64 folder
if exist Bin64 goto skip_bin64
echo Linking the server folder as Bin64
REM It must be the folder where SpaceEngineersDedicated.exe is located:
mklink /J Bin64 "%SE_SERVER_ROOT%\DedicatedServer64"
if %ERRORLEVEL% EQU 0 goto skip_bin64
echo ERROR: Missing Bin64 folder.
echo Please verify that Space Engineers Dedicated Server is installed.
echo If the Dedicated Server is installed at a custom location, then set the SE_SERVER_ROOT
echo environment variable to the server's root folder and try again.
goto failed
:skip_bin64

:: 11. Determine current game version and decide whether to wipe stale outputs
echo Checking current game version
uv run python -u check_version.py Bin64 Data > version_check.txt
if %ERRORLEVEL% EQU 0 (
    echo Game version unchanged - keeping existing decompilation
    goto skip_wipe
)
if %ERRORLEVEL% EQU 2 (
    echo Game version differs or no previous version recorded - wiping stale outputs
    if exist Data\Decompiled rmdir /s /q Data\Decompiled
    if exist Data\CodeIndex  rmdir /s /q Data\CodeIndex
    if exist Data\Content    rmdir /s /q Data\Content
    mkdir Data\Decompiled 2>NUL
    goto skip_wipe
)
echo ERROR: Failed to determine current game version
type version_check.txt
goto failed
:skip_wipe

:: 12. Decompile the server assemblies
if exist Data\Decompiled\VRage.XmlSerializers goto skip_decompile
.\busybox sh Decompile.sh
if %ERRORLEVEL% NEQ 0 goto failed

:: 12b. Fix case-collision folders (Gui vs GUI, Filesystem vs FileSystem)
echo Fixing case-collision folders
uv run python -u fix_case_collisions.py Data\Decompiled
if %ERRORLEVEL% NEQ 0 goto failed

:: 12a. Record the current game version and commit decompiled code
echo Recording game version and committing decompiled sources
uv run python -u check_version.py --write Bin64 Data
if %ERRORLEVEL% NEQ 0 goto failed

for /f "usebackq delims=" %%V in (`uv run python -u check_version.py --print Bin64`) do set "GAME_VERSION_LABEL=%%V"
if not defined GAME_VERSION_LABEL (
    echo ERROR: Could not determine game version label
    goto failed
)
echo Game version: !GAME_VERSION_LABEL!

pushd Data
git add -A
git -c user.name="se-dev-skills" -c user.email="se-dev-skills@localhost" commit -m "!GAME_VERSION_LABEL!"
if %ERRORLEVEL% NEQ 0 (
    echo (No commit made: working tree clean or nothing to commit)
)
popd
:skip_decompile

:: 13. Remove the Bin64 junction
rmdir /s /q Bin64

:: 14. Copy indexable content
if exist Data\Content goto skip_content
echo Copying indexable content
uv run python -u copy_content.py "%SE_SERVER_ROOT%\Content"
if %ERRORLEVEL% NEQ 0 goto failed
:skip_content

:: 15. Build the code index
if exist Data\CodeIndex\class_declarations.csv goto skip_code_index
echo Indexing decompiled code
mkdir Data\CodeIndex 2>NUL
uv run python -OO -u index_code.py Data\Decompiled Data\CodeIndex
if %ERRORLEVEL% NEQ 0 goto failed
:skip_code_index

:: 16. Build the content index
if exist Data\CodeIndex\content_index.csv goto skip_content_index
echo Indexing content files
uv run python -u index_content.py Data\Content Data\Decompiled Data\CodeIndex
if %ERRORLEVEL% NEQ 0 goto failed
:skip_content_index

if defined SE_DEV_SERVER_CODE_GRAPH_ROOT (
    set "SERVER_CODE_GRAPH_ROOT=%SE_DEV_SERVER_CODE_GRAPH_ROOT%"
) else (
    set "SERVER_CODE_GRAPH_ROOT=%CD%\Data\Decompiled"
)
call "%~dp0..\se-dev\GraphifyPrepare.bat" "se-dev-server-code" "%SERVER_CODE_GRAPH_ROOT%"

echo DONE
del version_check.txt 2>NUL
del "\\?\%cd%\nul" 2>error.txt
del error.txt
echo DONE >Prepare.DONE
exit /b 0

:failed
del version_check.txt 2>NUL
del "\\?\%cd%\nul" 2>error.txt
del error.txt
echo FAILED
exit /b 1
