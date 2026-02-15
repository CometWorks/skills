@echo off
:: Install skills for Claude Code
:: Target: %USERPROFILE%\.claude\skills

call "%~dp0helpers\install.bat" "%USERPROFILE%\.claude\skills"
