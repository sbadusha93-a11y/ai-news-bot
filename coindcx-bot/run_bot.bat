@echo off
cd /d "%~dp0"
echo Starting CoinDCX Signal Scanner...
echo Dashboard will be at http://127.0.0.1:8080
py coindcx_bot.py
pause
