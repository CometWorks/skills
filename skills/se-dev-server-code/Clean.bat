@echo off
rmdir /s /q __pycache__
rmdir /s /q CodeIndex
rmdir /s /q Content
rmdir /s /q Decompiled
rmdir /s /q .venv
del busybox.exe
del Prepare.log
del Prepare.DONE
exit /b 0
