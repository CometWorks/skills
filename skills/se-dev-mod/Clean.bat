@echo off
rmdir /s /q __pycache__
rmdir /s /q LocalMods
rmdir /s /q SteamMods
rmdir /s /q ModCodeIndex
rmdir /s /q .venv
del busybox.exe
del Prepare.log
del Prepare.DONE
exit /b 0
