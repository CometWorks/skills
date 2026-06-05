@echo off
:: Clean.bat - removes everything that Prepare.bat creates inside the skill
:: folder. The Data folder (a junction to %USERPROFILE%\.se-dev\torch) is
:: preserved: only the junction itself is removed so the actual contents
:: (Sources, CodeIndex) survive across runs.

if exist Data rmdir Data

if exist __pycache__ rmdir /s /q __pycache__
if exist .venv       rmdir /s /q .venv
if exist busybox.exe del busybox.exe
if exist Prepare.log del Prepare.log
if exist Prepare.DONE del Prepare.DONE
exit /b 0
