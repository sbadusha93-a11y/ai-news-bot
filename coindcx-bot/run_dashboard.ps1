$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
$py = "C:\Users\DELL\AppData\Local\Programs\Python\Launcher\py.exe"
"n`n" | & $py -3.13 -m streamlit run src/dashboard/app.py --server.port 8501 --server.headless true
