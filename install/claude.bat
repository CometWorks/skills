@echo off
REM Install skills for Claude Code
REM Target: %USERPROFILE%\.claude\skills

call "%~dp0helpers\install.bat" "%USERPROFILE%\.claude\skills"
