@echo off
cd /d "%~dp0"
echo Starting watchdog...
py watchdog.py
pause
