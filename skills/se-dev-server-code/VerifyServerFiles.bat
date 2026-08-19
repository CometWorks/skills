@echo off
setlocal EnableDelayedExpansion

REM VerifyServerFiles.bat - verify the installed Space Engineers Dedicated Server
REM files against the SHA256 digests recorded in Data\server_files.json. Windows
REM counterpart of verify_server_files.sh.
REM
REM Exit codes:
REM   0 = every server file matches the recorded hashes
REM   1 = error (server install or hash file not found)
REM   2 = files are missing, modified or extra
REM
REM Extra arguments are passed through to hash_server_files.py (e.g. -j 8, -q).

cd /d "%~dp0"

call "%~dp0DetectServerRoot.bat"
if %ERRORLEVEL% NEQ 0 exit /b 1
echo Server Root: %SE_SERVER_ROOT%

if exist Data\server_files.json goto have_hashes
echo ERROR: No recorded hashes in Data\server_files.json.
echo Run Prepare.bat first.
exit /b 1
:have_hashes

uv run python -u hash_server_files.py --verify "%SE_SERVER_ROOT%" Data %*
exit /b %ERRORLEVEL%
