pyinstaller --onefile --name=CoindcxBot --add-data "data_fetcher.py;." --add-data "indicators.py;." --add-data "scorer.py;." --add-data "display.py;." --hidden-import=win10toast --hidden-import=pandas --hidden-import=numpy coindcx_bot.py

echo.
echo ========================================
echo Build complete!
echo CoindcxBot.exe is in the current folder
echo ========================================
pause
