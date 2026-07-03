@echo off
setlocal EnableExtensions

echo Verifying Python
python --version
if %ERRORLEVEL% EQU 0 goto has_python
echo ERROR: Missing Python
echo Please install Python 3.11 or newer.
echo Make sure python.exe is on PATH.
goto failed
:has_python

echo Verifying git
git --version
if %ERRORLEVEL% EQU 0 goto has_git
echo ERROR: Missing git
echo Please install git for Windows from https://git-scm.com/download/win
echo Make sure git.exe is on PATH.
goto failed
:has_git

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
if %ERRORLEVEL% NEQ 0 goto failed
:skip_venv

if exist busybox.exe goto skip_busybox
echo Downloading busybox
powershell -Command "$ProgressPreference = 'SilentlyContinue'; Invoke-WebRequest -Uri https://frippery.org/files/busybox/busybox64u.exe -OutFile busybox.exe"
if %ERRORLEVEL% NEQ 0 goto failed
:skip_busybox

set "DATA_ROOT=%USERPROFILE%\.se-dev\torch"
echo Data Root: %DATA_ROOT%
if not exist "%DATA_ROOT%" (
    echo Creating Data Root folder
    mkdir "%DATA_ROOT%"
    if %ERRORLEVEL% NEQ 0 goto failed
)

if exist Data goto skip_data_junction
echo Linking the Data folder
mklink /J Data "%DATA_ROOT%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Could not create Data junction.
    goto failed
)
:skip_data_junction

if not exist Data\Sources mkdir Data\Sources
if not exist Data\CodeIndex mkdir Data\CodeIndex

if defined TORCH_ROOT goto use_local

set "TORCH_CLONE=Data\Sources\Torch"
if exist "%TORCH_CLONE%\.git" goto update_clone
if exist "%TORCH_CLONE%" goto bad_clone_dir
echo Cloning TorchAPI/Torch
git clone https://github.com/TorchAPI/Torch.git "%TORCH_CLONE%"
if %ERRORLEVEL% NEQ 0 goto failed
goto set_clone_root

:update_clone
echo Updating Torch checkout
git -C "%TORCH_CLONE%" pull --ff-only
if %ERRORLEVEL% NEQ 0 goto failed

:set_clone_root
for %%I in ("%TORCH_CLONE%") do set "TORCH_SOURCE=%%~fI"
echo Using cloned Torch checkout: %TORCH_SOURCE%
goto have_source

:bad_clone_dir
echo ERROR: %TORCH_CLONE% exists but is not a git checkout.
goto failed

:use_local
if not exist "%TORCH_ROOT%\Torch.sln" (
    echo ERROR: TORCH_ROOT must point at the Torch repository root containing Torch.sln
    goto failed
)
for %%I in ("%TORCH_ROOT%") do set "TORCH_SOURCE=%%~fI"
echo Using local Torch checkout: %TORCH_SOURCE%

:have_source
>Data\torch_root.txt echo %TORCH_SOURCE%

echo Indexing Torch source
uv run python -u index_torch.py
if %ERRORLEVEL% NEQ 0 goto failed

if defined SE_DEV_TORCH_PLUGIN_ROOT (
    set "TORCH_GRAPH_ROOT=%SE_DEV_TORCH_PLUGIN_ROOT%"
) else (
    set "TORCH_GRAPH_ROOT=%TORCH_SOURCE%"
)
call "%~dp0..\se-dev\GraphifyPrepare.bat" "se-dev-torch" "%TORCH_GRAPH_ROOT%"

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
