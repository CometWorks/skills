@echo off
setlocal EnableDelayedExpansion

REM 1. Detect game install location (env var override takes precedence)
if defined SE_GAME_ROOT goto have_game_root

REM Try the game's registry key
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

REM 2. Verify Python is available
echo Verifying Python
python --version
if %ERRORLEVEL% EQU 0 goto has_python
echo ERROR: Missing Python
echo Please install Python 3.11 or newer.
echo Make sure python.exe is on PATH.
goto failed
:has_python

REM 3. Verify command line git is available
echo Verifying git
git --version
if %ERRORLEVEL% EQU 0 goto has_git
echo ERROR: Missing git
echo Please install git for Windows from https://git-scm.com/download/win
echo Make sure git.exe is on PATH.
goto failed
:has_git

REM 4. Install uv if missing
uv -V 2>NUL
if %ERRORLEVEL% EQU 0 goto skip_uv
echo Installing uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv -V
if %ERRORLEVEL% NEQ 0 goto failed
:skip_uv

REM 5. Set up Python venv
if exist .venv goto skip_venv
echo Setting up Python .venv (uv sync)
uv sync
:skip_venv

REM 6. Download busybox if missing
if exist busybox.exe goto skip_busybox
echo Downloading busybox
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://frippery.org/files/busybox/busybox64u.exe -OutFile busybox.exe"
if %ERRORLEVEL% NEQ 0 goto failed
:skip_busybox

REM 7. Install ILSpy if missing
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

REM 8. Set up the Data folder under %USERPROFILE% and create a Data junction.
REM Using %USERPROFILE% rather than %LOCALAPPDATA% keeps the data outside the
REM UWP filesystem virtualization layer (Claude Code is a packaged app whose
REM writes under %LOCALAPPDATA% would be silently redirected into its
REM per-package LocalCache, hiding the data from regular tools).
set "DATA_ROOT=%USERPROFILE%\.se-dev\game-code"
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

REM 9. Initialize a local Git repository in the Data folder if missing
if exist Data\.git goto skip_git_init
echo Initializing local Git repository in the Data folder
pushd Data
REM Create the repository with 'main' as the default branch. The -c option sets the
REM initial branch on modern git (>=2.28) and suppresses git's "using master" hint.
git -c init.defaultBranch=main init
if %ERRORLEVEL% NEQ 0 (
    popd
    goto failed
)
REM Ensure default branch is main (fallback for git older than 2.28)
git symbolic-ref HEAD refs/heads/main 2>NUL

REM Required: some decompiled paths exceed the legacy MAX_PATH (260 chars),
REM e.g. EmptyKeys generated bindings under SpaceEngineers.Game.
git config core.longpaths true

REM Write .gitignore (Data\Content is versioned, so no Content/ entry)
> .gitignore (
    echo CodeIndex/
    echo graphify-out/
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

REM 10. Link the game's Bin64 folder
if exist Bin64 goto skip_bin64
echo Linking the game folder as Bin64
REM It must be the folder where SpaceEngineers.exe is located:
mklink /J Bin64 "%SE_GAME_ROOT%\Bin64"
if %ERRORLEVEL% EQU 0 goto skip_bin64
echo ERROR: Missing Bin64 folder.
echo Please verify that Space Engineers (version 1) is installed.
echo If Space Engineers is installed at a custom location, then set the SE_GAME_ROOT
echo environment variable to the game's root folder and try again.
goto failed
:skip_bin64

REM 11. Determine current game version and decide whether to wipe stale outputs
echo Checking current game version
uv run python -u check_version.py Bin64 Data > version_check.txt
if %ERRORLEVEL% EQU 0 (
    echo Game version unchanged - keeping existing decompilation
    goto skip_wipe
)
if %ERRORLEVEL% EQU 2 (
    echo Game version differs or no previous version recorded - wiping stale outputs
    REM Data files are incomplete until preparation finishes for the new game version
    if exist Prepare.DONE del Prepare.DONE
    if exist Data\Decompiled rmdir /s /q Data\Decompiled
    if exist Data\CodeIndex  rmdir /s /q Data\CodeIndex
    if exist Data\Content    rmdir /s /q Data\Content
    if exist Data\graphify-out rmdir /s /q Data\graphify-out
    mkdir Data\Decompiled 2>NUL
    goto skip_wipe
)
echo ERROR: Failed to determine current game version
type version_check.txt
goto failed
:skip_wipe

REM 12. Bring the Data folder up to the current layout before anything reads it.
REM Decompiled holds only decompiled C# code; Content and graphify-out sit beside
REM it. Earlier versions of this skill kept both inside Decompiled.
set NEED_COMMIT=0
if not exist Data\Decompiled\Content goto skip_move_content
echo Moving Data\Decompiled\Content up to Data\Content
if exist Data\Content rmdir /s /q Data\Content
move /Y Data\Decompiled\Content Data\Content >NUL
if %ERRORLEVEL% NEQ 0 goto failed
set NEED_COMMIT=1
:skip_move_content

if not exist Data\Decompiled\graphify-out goto skip_move_graph
if exist Data\graphify-out (
    rmdir /s /q Data\Decompiled\graphify-out
) else (
    echo Moving Data\Decompiled\graphify-out up to Data\graphify-out
    move /Y Data\Decompiled\graphify-out Data\graphify-out >NUL
)
:skip_move_graph

REM Content is versioned, so it must not be ignored (older installs ignored it).
findstr /X /L /C:"Content/" Data\.gitignore >NUL 2>NUL
if %ERRORLEVEL% EQU 0 (
    findstr /X /L /V /C:"Content/" Data\.gitignore >Data\.gitignore.tmp
    move /Y Data\.gitignore.tmp Data\.gitignore >NUL
    set NEED_COMMIT=1
)

REM The Graphify graph is a large regenerable artifact, so it must be ignored.
REM This has to be in place before the commit below, which stages everything.
REM Redirection precedes echo to avoid a trailing space in the line.
findstr /X /L /C:"graphify-out/" Data\.gitignore >NUL 2>NUL
if %ERRORLEVEL% NEQ 0 (
    >>Data\.gitignore echo graphify-out/
    set NEED_COMMIT=1
)

REM 13. Decompile the game assemblies
if exist Data\Decompiled\VRage.XmlSerializers goto skip_decompile
.\busybox sh Decompile.sh
if %ERRORLEVEL% NEQ 0 goto failed

REM Fix case-collision folders (Gui vs GUI, Filesystem vs FileSystem)
echo Fixing case-collision folders
uv run python -u fix_case_collisions.py Data\Decompiled
if %ERRORLEVEL% NEQ 0 goto failed
set NEED_COMMIT=1
:skip_decompile

REM 14. Copy indexable content. Only the indexable text files are copied (no
REM binaries), so the definition files can be versioned and their changes
REM reviewed.
if exist Data\Content goto skip_content
echo Copying indexable content
uv run python -u copy_content.py "%SE_GAME_ROOT%\Content"
if %ERRORLEVEL% NEQ 0 goto failed
set NEED_COMMIT=1
:skip_content

REM 15. Record the current game version and commit decompiled code and content
if "!NEED_COMMIT!"=="0" goto skip_commit
echo Recording game version and committing decompiled sources and content
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
:skip_commit

REM 16. Remove the Bin64 junction
rmdir /s /q Bin64

REM 17. Build the code index
if exist Data\CodeIndex\class_declarations.csv goto skip_code_index
echo Indexing decompiled code
mkdir Data\CodeIndex 2>NUL
uv run python -OO -u index_code.py Data\Decompiled Data\CodeIndex
if %ERRORLEVEL% NEQ 0 goto failed
:skip_code_index

REM 18. Build the content index
if exist Data\CodeIndex\content_index.csv goto skip_content_index
echo Indexing content files
uv run python -u index_content.py Data\Content Data\Decompiled Data\CodeIndex
if %ERRORLEVEL% NEQ 0 goto failed
:skip_content_index

REM Only the decompiled C# code is graphed; the graph itself is written beside it
REM (Data\graphify-out) so it never pollutes the graphed tree or the repository.
if defined SE_DEV_GAME_CODE_GRAPH_ROOT (
    set "GAME_CODE_GRAPH_ROOT=%SE_DEV_GAME_CODE_GRAPH_ROOT%"
) else (
    set "GAME_CODE_GRAPH_ROOT=%CD%\Data\Decompiled"
)
if defined SE_DEV_GAME_CODE_GRAPH_OUT (
    set "GAME_CODE_GRAPH_OUT=%SE_DEV_GAME_CODE_GRAPH_OUT%"
) else (
    set "GAME_CODE_GRAPH_OUT=%CD%\Data"
)
call "%~dp0..\se-dev\GraphifyPrepare.bat" "se-dev-game-code" "%GAME_CODE_GRAPH_ROOT%" "%GAME_CODE_GRAPH_OUT%"

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
