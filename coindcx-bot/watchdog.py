import os
import sys
import time
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "watchdog.log")
CHECK_INTERVAL = 60
HTTP_URL = "http://127.0.0.1:8080/"
BOT_SCRIPT = os.path.join(BASE_DIR, "run_bot.py")
bot_process = None
restart_count = 0


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_http_alive():
    try:
        r = urllib.request.urlopen(HTTP_URL, timeout=5)
        return r.status == 200
    except (urllib.error.URLError, Exception):
        return False


def start_bot():
    global bot_process
    try:
        bot_process = subprocess.Popen(
            [sys.executable, "-u", BOT_SCRIPT],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        log(f"Bot started (PID: {bot_process.pid})")
        return True
    except Exception as e:
        log(f"Failed to start bot: {e}")
        return False


def stop_bot():
    global bot_process
    if bot_process and bot_process.poll() is None:
        try:
            bot_process.terminate()
            bot_process.wait(timeout=5)
            log("Bot terminated")
        except Exception:
            try:
                bot_process.kill()
                bot_process.wait(timeout=3)
                log("Bot killed")
            except Exception:
                pass
    bot_process = None


def is_process_alive():
    if bot_process is None:
        return False
    return bot_process.poll() is None


def main():
    global restart_count
    log("=" * 50)
    log("Watchdog started")
    log(f"Check interval: {CHECK_INTERVAL}s")
    log(f"Bot script: {BOT_SCRIPT}")
    log("=" * 50)

    start_bot()
    last_restart = 0

    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            now = time.time()
            http_ok = is_http_alive()
            proc_ok = is_process_alive()

            if http_ok and proc_ok:
                continue

            if not http_ok:
                log(f"WARNING: HTTP endpoint not responding (checking /data)...")
            if not proc_ok:
                log(f"WARNING: Bot process not running (PID: {bot_process.pid if bot_process else 'N/A'})")

            cooldown = 30
            if now - last_restart < cooldown:
                log(f"Cooldown period ({cooldown}s), skipping restart")
                if not proc_ok:
                    start_bot()
                continue

            log("Initiating restart...")
            stop_bot()
            time.sleep(2)
            ok = start_bot()
            if ok:
                restart_count += 1
                last_restart = now
                log(f"Restart #{restart_count} complete")
            else:
                log(f"Restart #{restart_count + 1} FAILED")

        except KeyboardInterrupt:
            log("Watchdog shutting down...")
            stop_bot()
            break
        except Exception as e:
            log(f"Watchdog error: {e}")
            time.sleep(10)


if __name__ == "__main__":
    main()
