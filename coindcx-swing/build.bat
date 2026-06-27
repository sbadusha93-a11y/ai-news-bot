pyinstaller --onefile --name=Coindcx_Swing --distpath . --hidden-import=win10toast --hidden-import=pandas --hidden-import=numpy --hidden-import=requests --hidden-import=rich coindcx_swing.py
echo.
echo ========================================
echo Build complete!
echo Coindcx_Swing.exe is in the current folder
echo ========================================
pause
