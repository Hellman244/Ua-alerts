@echo off
cd /d "%~dp0"

rem The existing .venv was made for Linux, so Windows uses a separate .venv-win.
if exist ".venv-win\Scripts\python.exe" goto run

echo First run: creating environment and installing dependencies...
where py >nul 2>nul
if errorlevel 1 goto trypython
py -3 -m venv .venv-win
goto checkvenv
:trypython
python -m venv .venv-win
:checkvenv
if exist ".venv-win\Scripts\python.exe" goto install
echo Could not create the environment. Install Python 3.12+ and try again.
pause
exit /b 1

:install
".venv-win\Scripts\python.exe" -m pip install --upgrade pip
".venv-win\Scripts\python.exe" -m pip install -r "ua_alert\requirements.txt"
if errorlevel 1 goto installfail
goto run
:installfail
echo Failed to install dependencies.
rmdir /s /q ".venv-win"
pause
exit /b 1

:run
rem Starts without a console window. Demo mode: start_ua_alert.bat --simulate
start "" ".venv-win\Scripts\pythonw.exe" -m ua_alert.main %*
