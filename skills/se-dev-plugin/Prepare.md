1. Run `python --version`, if it fails or not at least 3.11 then inform the user and stop here.
2. Inform the user that this is a one time preparation which will take about 1 minute.
3. On Windows run `.\Prepare.bat >Prepare.log 2>&1`. On Linux/macOS run `./prepare.sh >Prepare.log 2>&1`. Use this same folder as CWD, this is where `Prepare.md` is situated.
4. The preparation is successful if the last line of `Prepare.log` is `DONE`. If it fails, inform the user and stop here.
