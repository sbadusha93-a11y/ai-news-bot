@echo off
cd /d "C:\Users\DELL\Desktop\playwright-demo\ai-news-bot"

if not exist logs mkdir logs

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set dt=%%I
set timestamp=%dt:~0,4%%dt:~4,2%%dt:~6,2%_%dt:~8,2%%dt:~10,2%

py -3 ai_news_bot.py --upload --privacy unlisted >> "logs\run_%timestamp%.log" 2>&1
