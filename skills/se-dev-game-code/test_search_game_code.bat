@echo off
setlocal EnableExtensions
cd /d "%~dp0"

REM Code search smoke test for the decompiled game code index (Windows).
REM
REM The checks themselves live in test_search_code.py so that Windows and Linux
REM run exactly the same assertions. Exits non-zero if any check failed.

uv run test_search_code.py
exit /b %ERRORLEVEL%
