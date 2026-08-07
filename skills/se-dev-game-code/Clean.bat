@echo off
REM Clean.bat - removes everything that Prepare.bat creates inside the skill
REM folder. The Data folder (a junction to %USERPROFILE%\.se-dev\game-code)
REM is preserved: only the junction itself is removed so the
REM actual contents (Decompiled, CodeIndex, Content, .git) survive across runs.

REM Remove the Data junction (NOT its contents - rmdir without /s deletes only
REM the junction reparse point and leaves the target folder intact).
if exist Data rmdir Data

REM Remove the Bin64 junction (also leaves the actual game install untouched).
if exist Bin64 rmdir Bin64

REM Remove transient skill artefacts.
if exist __pycache__   rmdir /s /q __pycache__
if exist .venv         rmdir /s /q .venv
if exist busybox.exe   del busybox.exe
if exist Decompile.log del Decompile.log
if exist Prepare.log   del Prepare.log
if exist Prepare.DONE  del Prepare.DONE
if exist version_check.txt del version_check.txt

exit /b 0
