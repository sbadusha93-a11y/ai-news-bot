import time
import winsound
import os
import sys
from datetime import datetime
from threading import Thread

from rich.console import Console
from rich.table import Table
from rich import box

import warnings
warnings.filterwarnings("ignore")

from plyer import notification


_NOTIFIED = {}
_THROTTLE_SECONDS = 300


def _is_throttled(key):
    now = time.time()
    if key in _NOTIFIED and now - _NOTIFIED[key] < _THROTTLE_SECONDS:
        return True
    _NOTIFIED[key] = now
    return False


def send_notification(title, message, sound_type="info"):
    key = f"{title}|{message}"
    if _is_throttled(key):
        return

    def _notify():
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5,
                app_name="CoinDCX Scanner",
            )
            beep_map = {"info": (800, 200), "success": (1000, 300), "warn": (600, 400), "error": (400, 500)}
            freq, dur = beep_map.get(sound_type, (800, 200))
            try:
                winsound.Beep(freq, dur)
                if sound_type in ("success", "error"):
                    time.sleep(0.15)
                    winsound.Beep(freq, dur)
            except Exception:
                print("\a", end="", flush=True)
        except Exception:
            pass

    Thread(target=_notify, daemon=True).start()


class LiveDisplay:
    def __init__(self):
        self.console = Console()
        self._prev_signals = {}

    def detect_and_notify(self, rows):
        for r in rows:
            coin = r["coin"]
            direction = r["direction"]
            prev = self._prev_signals.get(coin, "NONE")
            current = direction

            if prev != current:
                price = r["price"]
                if current == "LONG":
                    send_notification(
                        f"BUY SIGNAL: {coin}",
                        f"Checks: {r['long_pct']}% | R:R {r['rr']}",
                        "success"
                    )
                elif current == "SHORT":
                    send_notification(
                        f"SELL SIGNAL: {coin}",
                        f"Checks: {r['short_pct']}% | R:R {r['rr']}",
                        "warn"
                    )
                elif current == "NONE" and prev in ("LONG", "SHORT"):
                    send_notification(f"CLOSED: {coin}", f"Signal lost for {coin}", "info")

            reasons = r.get("exit_reasons", [])
            if reasons and prev in ("LONG", "SHORT"):
                reason = reasons[0]
                exit_key = f"{coin}_EXIT_{reason}"
                if not _is_throttled(exit_key):
                    price = r["price"]
                    entry = r.get("entry", price)
                    if prev == "LONG":
                        pnl_pct = ((price - entry) / entry) * 100
                    else:
                        pnl_pct = ((entry - price) / entry) * 100
                    emoji = "GREEN" if pnl_pct >= 0 else "RED"
                    send_notification(
                        f"EXIT: {coin} \u2014 {reason}",
                        f"Exit Price:  | P&L: {pnl_pct:+.2f}% {emoji}",
                        "success" if pnl_pct >= 0 else "error"
                    )

            self._prev_signals[coin] = current
