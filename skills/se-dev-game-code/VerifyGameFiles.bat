@echo off
setlocal EnableDelayedExpansion

REM VerifyGameFiles.bat - verify the installed Space Engineers files against the
REM SHA256 digests recorded in Data\game_files.json. Windows counterpart of
REM verify_game_files.sh.
REM
REM Exit codes:
REM   0 = every game file matches the recorded hashes
REM   1 = error (game install or hash file not found)
REM   2 = files are missing, modified or extra
REM
REM Extra arguments are passed through to hash_game_files.py (e.g. -j 8, -q).

cd /d "%~dp0"

call "%~dp0DetectGameRoot.bat"
if %ERRORLEVEL% NEQ 0 exit /b 1
echo Game Root: %SE_GAME_ROOT%

if exist Data\game_files.json goto have_hashes
echo ERROR: No recorded hashes in Data\game_files.json.
echo Run Prepare.bat first.
exit /b 1
:have_hashes

uv run python -u hash_game_files.py --verify "%SE_GAME_ROOT%" Data %*
exit /b %ERRORLEVEL%
