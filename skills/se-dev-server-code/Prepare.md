1. Run `python --version`, if it fails or not at least 3.13 then inform the user and stop here.
2. Inform the user that this is a one time preparation which will take about 5-15 minutes. Highlight this message.
3. Run `.\Prepare.bat >Prepare.log 2>&1` with this same folder as CWD, this is where `Prepare.md` is situated.
4. The preparation is successful if the last line of `Prepare.log` is `DONE`. If it fails, inform the user and stop here.
