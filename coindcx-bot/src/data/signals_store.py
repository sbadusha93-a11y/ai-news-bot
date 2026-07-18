import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SIGNALS_FILE = Path(__file__).parent.parent.parent / "data" / "latest_signals.json"


def get_signals_file() -> Path:
    SIGNALS_FILE.parent.mkdir(parents=True, exist_ok=True)
    return SIGNALS_FILE


def save_bot_signals(ranked: List[Dict]):
    expiry_ts = int(datetime.now(timezone.utc).timestamp()) + 3600
    signals = []
    for opp in ranked:
        tf_key = list(opp.get("analysis", {}).get("timeframes", {}).keys())
        tf_data = opp.get("analysis", {}).get("timeframes", {})
        primary_tf = tf_key[0] if tf_key else "4h"
        last_row = tf_data.get(primary_tf, {}).get("last_row", {})
        primary_data = tf_data.get(primary_tf, {})

        close = last_row.get("close", 0)
        atr = last_row.get("atr", 0)
        rsi = last_row.get("rsi", 50)
        adx = last_row.get("adx", 0)
        direction = opp.get("direction", "neutral")

        sl = None
        tp1 = tp2 = tp3 = None
        if direction == "long":
            sl = close - (atr * 1.5) if atr > 0 else close * 0.95
            tp1 = close + (abs(close - sl) * 2.0) if sl else close * 1.05
            tp2 = close + (abs(close - sl) * 3.5) if sl else close * 1.08
            tp3 = close + (abs(close - sl) * 5.0) if sl else close * 1.12
        elif direction == "short":
            sl = close + (atr * 1.5) if atr > 0 else close * 1.05
            tp1 = close - (abs(close - sl) * 2.0) if sl else close * 0.95
            tp2 = close - (abs(close - sl) * 3.5) if sl else close * 0.92
            tp3 = close - (abs(close - sl) * 5.0) if sl else close * 0.88

        signal = "LONG" if direction == "long" else "SHORT" if direction == "short" else "NEUTRAL"
        signals.append({
            "symbol": opp["symbol"],
            "signal": signal,
            "confidence": opp.get("confidence", 50),
            "entry_price": close,
            "current_price": close,
            "sl_price": sl,
            "tp1_price": tp1,
            "tp2_price": tp2,
            "tp3_price": tp3,
            "trend": last_row.get("st_direction", "neutral"),
            "rsi": rsi if rsi else 50,
            "macd_dir": last_row.get("macd_signal_line", "neutral"),
            "adx": adx if adx else 0,
            "bos": last_row.get("bos", "none"),
            "choch": last_row.get("choch", "none"),
            "expiry_ts": expiry_ts,
            "scanned_at": int(datetime.now(timezone.utc).timestamp()),
            "from_bot": True,
        })
    try:
        get_signals_file().write_text(
            json.dumps({"signals": signals, "updated_at": int(time.time())}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


def load_bot_signals() -> List[Dict]:
    try:
        f = get_signals_file()
        if not f.exists():
            return []
        raw = json.loads(f.read_text(encoding="utf-8"))
        data = raw if isinstance(raw, list) else raw.get("signals", [])
        updated = raw.get("updated_at", 0) if isinstance(raw, dict) else 0
        if time.time() - updated > 300:
            return []
        return [s for s in data if s.get("from_bot")]
    except Exception:
        return []
