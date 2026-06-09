@echo off
setlocal enabledelayedexpansion

:: Space Engineers Developer Skills - Installation Script
:: Usage: install.bat <target_skills_folder>
:: Creates junction points for all skills in the target folder

if "%~1"=="" (
    echo Usage: install.bat ^<target_skills_folder^>
    echo Example: install.bat "%%USERPROFILE%%\.claude\skills"
    exit /b 1
)

set "TARGET=%~1"

:: Get the absolute path to the skills folder (relative to this script's location)
set "SCRIPT_DIR=%~dp0"
set "SKILLS_DIR=%SCRIPT_DIR%\..\skills"

:: Convert to absolute path
pushd "%SKILLS_DIR%"
set "SKILLS_DIR=%CD%"
popd

echo Installing Space Engineers Developer Skills
echo Source: %SKILLS_DIR%
echo Target: %TARGET%
echo.

:: Create target folder if it doesn't exist
if not exist "%TARGET%" (
    echo Creating target folder: %TARGET%
    mkdir "%TARGET%"
    if errorlevel 1 (
        echo ERROR: Failed to create target folder
        exit /b 1
    )
)

:: List of skills to install
set "SKILLS=se-dev-game-code se-dev-mod se-dev-plugin se-dev-torch se-dev-script se-dev-server-code"

set "SUCCESS=0"
set "FAILED=0"

for %%S in (%SKILLS%) do (
    set "LINK=%TARGET%\%%S"
    set "SOURCE=%SKILLS_DIR%\%%S"

    if exist "!LINK!" (
        echo [SKIP] %%S - already exists
    ) else (
        echo [INSTALL] %%S
        mklink /J "!LINK!" "!SOURCE!"
        if errorlevel 1 (
            echo   ERROR: Failed to create junction point
            echo   You may need to run this script as Administrator
            set /a FAILED+=1
        ) else (
            set /a SUCCESS+=1
        )
    )
)

echo.
echo Installation complete: %SUCCESS% installed, %FAILED% failed
if %FAILED% gtr 0 (
    echo.
    echo Some installations failed. Try running as Administrator.
    exit /b 1
)

exit /b 0
