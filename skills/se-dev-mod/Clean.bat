@echo off
:: Clean.bat - removes everything that Prepare.bat creates inside the skill
:: folder. The Data folder (a junction to %USERPROFILE%\.se-dev\mod) is
:: preserved: only the junction itself is removed so the actual contents
:: (CodeIndex, mods.json, mod_hashes.json) survive across runs.

if exist Data      rmdir Data
if exist LocalMods rmdir LocalMods

if exist __pycache__ rmdir /s /q __pycache__
if exist .venv       rmdir /s /q .venv
if exist busybox.exe del busybox.exe
if exist Prepare.log del Prepare.log
if exist Prepare.DONE del Prepare.DONE
exit /b 0
