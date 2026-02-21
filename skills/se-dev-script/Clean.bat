@echo off
rmdir /s /q __pycache__
rmdir /s /q LocalScripts
rmdir /s /q SteamScripts
rmdir /s /q ScriptCodeIndex
rmdir /s /q .venv
del busybox.exe
del Prepare.log
del Prepare.DONE
exit /b 0
