import sys, os, time, subprocess, json, urllib.request, urllib.error

PUBLIC = "https://public.coindcx.com"
BOT_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_bot.py")

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def fetch_4h_candle():
    url = f"{PUBLIC}/market_data/candles?pair=B-BTC_USDT&interval=4h&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "CoindcxBot/1.0"})
    try:
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read().decode())
        if data and len(data) > 0:
            return data[-1]
    except Exception as e:
        log(f"API error: {e}")
    return None

def is_candle_fresh(candle):
    candle_time_ms = float(candle["time"])
    candle_open = candle_time_ms / 1000
    now = time.time()
    elapsed = now - candle_open
    return elapsed < 14400  # within current 4h window

def kill_bot():
    killed = False
    for proc in subprocess.check_output("tasklist", shell=True).decode().splitlines():
        if "python" in proc.lower():
            pid = None
            parts = proc.split()
            for p in parts:
                if p.isdigit():
                    pid = int(p)
                    break
            if pid:
                try:
                    cmdline = subprocess.check_output(f'wmic process where ProcessId={pid} get CommandLine', shell=True).decode()
                    if "run_bot.py" in cmdline or "coindcx_bot.py" in cmdline:
                        subprocess.run(f"taskkill /PID {pid} /F", shell=True, capture_output=True)
                        log(f"Killed bot PID {pid}")
                        killed = True
                except:
                    pass
    return killed

log("Checking 4H candle freshness...")
candle = fetch_4h_candle()
if not candle:
    log("Failed to fetch 4H candle. Aborting.")
    sys.exit(1)

log(f"Latest BTC 4H candle time: {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(candle['time'])/1000))}")

if not is_candle_fresh(candle):
    log("Candle data is stale (older than 4h). Aborting restart.")
    sys.exit(1)

log("4H candle data is fresh. Proceeding with restart...")
kill_bot()
time.sleep(2)
subprocess.Popen([sys.executable, BOT_SCRIPT], cwd=os.path.dirname(BOT_SCRIPT))
log("Bot restarted successfully.")
