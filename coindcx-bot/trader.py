import hashlib
import hmac
import json
import os
import time
import requests
from datetime import datetime
from data_fetcher import to_candle_pair

BASE = "https://api.coindcx.com"
session = requests.Session()
session.headers.update({"User-Agent": "CoindcxBot/1.0", "Content-Type": "application/json"})

_config = {}
_open_positions = {}
_trade_log = []
_completed_orders = []
_positions_file = ""
_trade_log_file = ""
_completed_file = ""
_last_save = 0
_dirty = False


def load_config(path="config.json"):
    global _config
    try:
        with open(path) as f:
            _config = json.load(f)
        _ensure_data_dir(path)
        load_positions()
        load_trade_log()
        load_completed_orders()
        return True
    except Exception as e:
        print(f"[trader] Failed to load config: {e}")
        return False


def reload_config(path="config.json"):
    result = load_config(path)
    load_positions()
    load_trade_log()
    load_completed_orders()
    return result


def _ensure_data_dir(config_path):
    global _positions_file, _trade_log_file, _completed_file
    data_dir = os.path.dirname(os.path.abspath(config_path))
    _positions_file = os.path.join(data_dir, "open_positions.json")
    _trade_log_file = os.path.join(data_dir, "trade_log.json")
    _completed_file = os.path.join(data_dir, "completed_orders.json")


def load_positions():
    global _open_positions
    try:
        if os.path.exists(_positions_file):
            with open(_positions_file) as f:
                loaded = json.load(f)
            _open_positions = loaded
            if loaded:
                print(f"[trader] Restored {len(loaded)} open position(s) from {_positions_file}")
    except Exception as e:
        print(f"[trader] Failed to load positions: {e}")


def save_positions():
    global _last_save, _dirty
    if not _dirty:
        return
    now = time.time()
    if now - _last_save < 5:
        return
    _last_save = now
    _dirty = False
    try:
        with open(_positions_file, "w") as f:
            json.dump(_open_positions, f, indent=2)
    except Exception as e:
        print(f"[trader] Failed to save positions: {e}")


def _save_positions_now():
    global _last_save, _dirty
    _last_save = time.time()
    _dirty = False
    try:
        with open(_positions_file, "w") as f:
            json.dump(_open_positions, f, indent=2)
    except Exception as e:
        print(f"[trader] Failed to save positions: {e}")


def load_trade_log():
    global _trade_log
    try:
        if os.path.exists(_trade_log_file):
            with open(_trade_log_file) as f:
                _trade_log = json.load(f)
    except Exception as e:
        print(f"[trader] Failed to load trade log: {e}")


def _save_trade_log():
    try:
        with open(_trade_log_file, "w") as f:
            json.dump(_trade_log, f, indent=2)
    except Exception as e:
        print(f"[trader] Failed to save trade log: {e}")


def load_completed_orders():
    global _completed_orders
    try:
        if os.path.exists(_completed_file):
            with open(_completed_file) as f:
                _completed_orders = json.load(f)
            if _completed_orders:
                print(f"[trader] Restored {len(_completed_orders)} completed order(s)")
    except Exception as e:
        print(f"[trader] Failed to load completed orders: {e}")


def _save_completed_orders():
    try:
        with open(_completed_file, "w") as f:
            json.dump(_completed_orders, f, indent=2)
    except Exception as e:
        print(f"[trader] Failed to save completed orders: {e}")


def _push_completed(entry):
    global _completed_orders
    _completed_orders.append(entry)
    if len(_completed_orders) > 100:
        _completed_orders = _completed_orders[-100:]
    _save_completed_orders()


def get_completed_orders():
    return list(reversed(_completed_orders))


def is_trading_enabled():
    return _config.get("auto_trade", False) and _config.get("api_key") and _config.get("api_secret") and _config.get("api_key") != "YOUR_API_KEY_HERE"


def is_paper_mode():
    return _config.get("trade_mode", "paper") == "paper"


def _sign(body):
    secret = _config.get("api_secret", "")
    payload = json.dumps(body, separators=(",", ":"))
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _api_post(endpoint, body):
    api_key = _config.get("api_key", "")
    signature = _sign(body)
    headers = {"X-AUTH-APIKEY": api_key, "X-AUTH-SIGNATURE": signature}
    try:
        r = session.post(f"{BASE}{endpoint}", json=body, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[trader] API POST {endpoint} failed: {e}")
        return None


def _api_get(endpoint):
    api_key = _config.get("api_key", "")
    ts = int(time.time() * 1000)
    body = {"timestamp": ts}
    signature = _sign(body)
    headers = {"X-AUTH-APIKEY": api_key, "X-AUTH-SIGNATURE": signature}
    try:
        r = session.post(f"{BASE}{endpoint}", json=body, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[trader] API GET {endpoint} failed: {e}")
        return None


def get_balances():
    data = _api_get("/exchange/v1/users/balances")
    if not data:
        return {}
    result = {}
    for item in data:
        currency = item.get("currency", "")
        balance = float(item.get("balance", 0))
        locked = float(item.get("locked_balance", 0))
        if balance > 0 or locked > 0:
            result[currency] = {"free": balance, "locked": locked, "total": balance + locked}
    return result


def get_usdt_balance():
    balances = get_balances()
    usdt = balances.get("USDT", {})
    return usdt.get("free", 0)


def get_futures_balance():
    api_key = _config.get("api_key", "")
    ts = int(time.time() * 1000)
    body = {"timestamp": ts}
    json_body = json.dumps(body, separators=(",", ":"))
    signature = hmac.new(_config.get("api_secret", "").encode("utf-8"), json_body.encode(), hashlib.sha256).hexdigest()
    headers = {"Content-Type": "application/json", "X-AUTH-APIKEY": api_key, "X-AUTH-SIGNATURE": signature}
    try:
        r = session.get(f"{BASE}/exchange/v1/derivatives/futures/wallets", data=json_body, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        for w in data:
            cur = w.get("currency_short_name", "")
            if cur in ("USDT", "INR"):
                bal = float(w.get("balance", 0))
                return bal, cur
        return 0, ""
    except Exception as e:
        print(f"[trader] Futures balance failed: {e}")
        return 0, ""


_inr_usdt_rate = None
_inr_rate_fetch_time = 0


def _get_inr_usdt_rate():
    global _inr_usdt_rate, _inr_rate_fetch_time
    now = time.time()
    if _inr_usdt_rate is not None and now - _inr_rate_fetch_time < 300:
        return _inr_usdt_rate
    try:
        r = session.get("https://api.coindcx.com/exchange/ticker", timeout=5)
        tickers = r.json()
        for t in tickers:
            if t.get("market") == "USDTINR":
                _inr_usdt_rate = float(t["last_price"])
                _inr_rate_fetch_time = now
                return _inr_usdt_rate
    except Exception as e:
        print(f"[trader] Failed to fetch INR rate: {e}")
    _inr_usdt_rate = 100.0
    return _inr_usdt_rate


def place_futures_order(side, pair, qty, leverage, tp_price=None, sl_price=None, margin_currency="USDT"):
    api_key = _config.get("api_key", "")
    ts = int(time.time() * 1000)
    order = {
        "side": side,
        "pair": pair,
        "order_type": "market_order",
        "total_quantity": str(qty),
        "leverage": int(leverage),
        "notification": "no_notification",
        "time_in_force": "good_till_cancel",
        "hidden": False,
        "post_only": False,
        "margin_currency_short_name": margin_currency,
    }
    if tp_price:
        order["take_profit"] = float(tp_price)
    if sl_price:
        order["stop_loss"] = float(sl_price)
    order["position_margin_type"] = "isolated"
    body = {"timestamp": ts, "order": order}
    signature = hmac.new(_config.get("api_secret", "").encode("utf-8"), json.dumps(body, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
    headers = {"Content-Type": "application/json", "X-AUTH-APIKEY": api_key, "X-AUTH-SIGNATURE": signature}
    try:
        payload = json.dumps(body, separators=(",", ":"))
        r = session.post(f"{BASE}/exchange/v1/derivatives/futures/orders/create", data=payload, headers=headers, timeout=10)
        if not r.ok:
            print(f"[trader] Futures order failed ({r.status_code}): {r.text[:500]}")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[trader] Futures order exception: {e}")
        return None


def _calc_quantity(price_usdt, max_usdt=None):
    if not max_usdt:
        max_usdt = _config.get("max_position_size_usdt", 10)
    if price_usdt <= 0:
        return 0
    qty = max_usdt / price_usdt
    return round(qty, 6)


def place_order(side, market, price, qty, order_type="limit"):
    if qty <= 0 or price <= 0:
        print(f"[trader] Invalid qty({qty}) or price({price}) for {market}")
        return None

    candle_pair = to_candle_pair(market)
    ts = int(time.time() * 1000)
    body = {
        "side": side,
        "order_type": order_type,
        "market": candle_pair,
        "price_per_unit": str(price),
        "total_quantity": qty,
        "timestamp": ts,
    }

    if is_paper_mode():
        fake_id = f"PAPER_{side}_{market}_{ts}"
        print(f"[trader][PAPER] {side.upper()} {qty} {market} @ {price} (ID: {fake_id})")
        return {"id": fake_id, "side": side, "market": market, "price": price, "qty": qty, "status": "PAPER_FILLED", "timestamp": ts}

    result = _api_post("/exchange/v1/orders/create", body)
    if result:
        order_id = result.get("id")
        print(f"[trader] {side.upper()} {qty} {market} @ {price} (ID: {order_id})")
        return {"id": order_id, "side": side, "market": market, "price": price, "qty": qty, "status": "SUBMITTED", "timestamp": ts}
    return None


def place_sl_order(market, side, qty, trigger_price):
    candle_pair = to_candle_pair(market)
    ts = int(time.time() * 1000)
    sl_side = "sell" if side == "buy" else "buy"
    body = {
        "side": sl_side,
        "order_type": "stop_limit",
        "market": candle_pair,
        "price_per_unit": str(trigger_price),
        "trigger_price": str(trigger_price),
        "total_quantity": qty,
        "timestamp": ts,
    }

    if is_paper_mode():
        fake_id = f"PAPER_SL_{market}_{ts}"
        print(f"[trader][PAPER] SL {sl_side.upper()} {qty} {market} @ {trigger_price} (ID: {fake_id})")
        return {"id": fake_id, "type": "SL", "status": "PAPER_ACTIVE", "timestamp": ts}

    result = _api_post("/exchange/v1/orders/create", body)
    if result:
        order_id = result.get("id")
        print(f"[trader] SL {sl_side.upper()} {qty} {market} @ {trigger_price} (ID: {order_id})")
        return {"id": order_id, "type": "SL", "status": "ACTIVE", "timestamp": ts}
    return None


def cancel_order(order_id):
    ts = int(time.time() * 1000)
    body = {"id": order_id, "timestamp": ts}
    result = _api_post("/exchange/v1/orders/cancel", body)
    return result is not None


def open_positions():
    data = _api_get("/exchange/v1/orders/active_open_orders")
    if not data:
        return []
    return data


def _log_trade(entry):
    global _trade_log
    _trade_log.append(entry)
    _trade_log = _trade_log[-50:]
    _save_trade_log()


def get_trade_log():
    return list(_trade_log)


def check_and_trade(signal_rows):
    if not is_trading_enabled():
        return []

    max_pos = _config.get("max_positions", 3)

    if is_paper_mode():
        usdt_avail = _config.get("max_position_size_usdt", 10) * (max_pos - len(_open_positions))
        min_ds = _config.get("min_ds_conf", 50)
        min_rr = _config.get("min_rr", 1.5)
        trades = []
        for r in signal_rows:
            if len(_open_positions) >= max_pos:
                break
            coin = r["coin"]
            if coin in _open_positions:
                continue
            if r.get("ds_conf", 0) < min_ds:
                continue
            if r.get("ds_conf", 0) < 75:
                continue
            if r.get("rr", 0) < min_rr:
                continue
            if r.get("persist", 0) < 3:
                continue
            if r.get("fund_pct", 0) < 60:
                continue
            if r.get("direction") not in ("LONG", "SHORT") and r.get("ds_conf", 0) < 75:
                continue
            dir_ = r["direction"]
            if dir_ not in ("LONG", "SHORT"):
                dir_ = "LONG" if (r.get("long_pct") or 0) >= (r.get("short_pct") or 0) else "SHORT"
            side = "buy" if dir_ == "LONG" else "sell"
            market = f"{coin}USDT"
            entry_price = r["entry"]
            qty = _calc_quantity(entry_price, min(usdt_avail, _config.get("max_position_size_usdt", 10)))
            if qty <= 0:
                continue
            order = place_order(side, market, entry_price, qty)
            if not order:
                continue
            _open_positions[coin] = {
                "coin": coin, "direction": dir_, "entry": entry_price,
                "target": r["target"], "sl": r["sl"], "atr_pct": r.get("atr_pct") or 0.5,
                "qty": qty, "order_id": order.get("id"),
                "entry_time": datetime.now().strftime("%H:%M:%S"),
            }
            _save_positions()
            trades.append(r)
        return trades

    futures_avail, margin_currency = get_futures_balance()
    if futures_avail <= 0:
        print("[trader] No futures balance available")
        return []

    if margin_currency == "INR":
        usdt_avail = futures_avail / _get_inr_usdt_rate()
    else:
        usdt_avail = futures_avail

    candidates = [r for r in signal_rows
                  if (r.get("direction") in ("LONG", "SHORT") or (r.get("direction") == "NONE" and r.get("ds_conf", 0) >= 75 and r.get("fund_pct", 0) >= 60))
                  and r.get("persist", 0) >= (1 if r.get("direction") == "NONE" else 3)
                   and r.get("ds_conf", 0) >= 75
                  and (r.get("fund_pct") or 0) >= 60
                  and r["coin"] not in _open_positions]
    if not candidates:
        return []

    candidates.sort(key=lambda r: (r.get("ds_conf", 0) or 0, r.get("fund_pct", 0) or 0), reverse=True)
    r = candidates[0]
    coin = r["coin"]
    dir_ = r["direction"]
    if dir_ not in ("LONG", "SHORT"):
        dir_ = "LONG" if (r.get("long_pct") or 0) >= (r.get("short_pct") or 0) else "SHORT"
    side = "buy" if dir_ == "LONG" else "sell"
    entry_price = r["entry"]
    pair = f"{coin}USDT"
    leverage = r.get("leverage", 5)
    if isinstance(leverage, str):
        try:
            leverage = int(leverage.replace("x", ""))
        except (ValueError, AttributeError):
            leverage = 5
    qty = _calc_quantity(entry_price, usdt_avail * 0.5)
    if qty <= 0:
        return []

    tp = r.get("target")
    sl = r.get("sl")
    order = place_futures_order(side, pair, qty, leverage, tp, sl, margin_currency)
    if not order:
        return []

    _open_positions[coin] = {
        "coin": coin, "direction": dir_, "entry": entry_price,
        "target": tp, "sl": sl, "atr_pct": r.get("atr_pct") or 0.5,
        "qty": qty, "order_id": order.get("id"),
        "entry_time": datetime.now().strftime("%H:%M:%S"),
    }
    _save_positions()
    print(f"[trader] Futures {dir_} {coin} | qty={qty} lev={leverage} entry={entry_price} tp={tp} sl={sl}")
    return [r]


def close_position(coin, current_price):
    pos = _open_positions.get(coin)
    if not pos:
        return None
    mode = "PAPER" if is_paper_mode() else "LIVE"
    if not is_paper_mode():
        side = "sell" if pos["direction"] == "LONG" else "buy"
        result = place_order(side, f"{coin}USDT", current_price, pos["qty"], "market")
        if not result:
            print(f"[trader] FAILED to manually close {coin} {pos['direction']} - market order rejected")
            return None
    pnl = (current_price - pos["entry"]) / pos["entry"] * 100
    if pos["direction"] == "SHORT":
        pnl = -pnl
    pnl_val = round((pnl / 100) * pos["qty"] * pos["entry"], 2)
    log_entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "mode": mode,
        "coin": coin,
        "direction": pos["direction"],
        "entry": pos["entry"],
        "exit": current_price,
        "pnl": round(pnl, 2),
        "pnl_value": pnl_val,
        "qty": pos["qty"],
        "reason": "MANUAL",
        "status": "CLOSED",
    }
    _log_trade(log_entry)
    _push_completed(log_entry)
    del _open_positions[coin]
    _save_positions_now()
    return log_entry


def get_positions_with_pnl(current_prices):
    result = []
    for coin, pos in _open_positions.items():
        p = pos.copy()
        price = current_prices.get(coin)
        p["original_sl"] = p["sl"]
        if price:
            pnl = (price - p["entry"]) / p["entry"] * 100
            if p["direction"] == "SHORT":
                pnl = -pnl
            p["live_price"] = price
            p["pnl"] = round(pnl, 2)
        else:
            p["live_price"] = None
            p["pnl"] = None
        result.append(p)
    return result


def check_exits(current_prices):
    exited = []
    for coin, pos in list(_open_positions.items()):
        price = current_prices.get(coin)
        if not price:
            continue

        reason = None
        if pos["direction"] == "LONG":
            if pos["target"] and price >= pos["target"]:
                reason = "TP HIT"
            elif pos["sl"] and price <= pos["sl"]:
                reason = "SL HIT"
        else:
            if pos["target"] and price <= pos["target"]:
                reason = "TP HIT"
            elif pos["sl"] and price >= pos["sl"]:
                reason = "SL HIT"

        if reason:
            mode = "PAPER" if is_paper_mode() else "LIVE"
            if not is_paper_mode():
                result = place_order("sell" if pos["direction"] == "LONG" else "buy", f"{coin}USDT", price, pos["qty"], "market")
                if not result:
                    print(f"[trader] FAILED to close {coin} {pos['direction']} at {price} - market order rejected. Keeping position.")
                    continue

            pnl = (price - pos["entry"]) / pos["entry"] * 100
            if pos["direction"] == "SHORT":
                pnl = -pnl
            pnl_val = round((pnl / 100) * pos["qty"] * pos["entry"], 2)

            log_entry = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "mode": mode,
                "coin": coin,
                "direction": pos["direction"],
                "entry": pos["entry"],
                "exit": price,
                "pnl": round(pnl, 2),
                "pnl_value": pnl_val,
                "qty": pos["qty"],
                "reason": reason,
                "status": "CLOSED",
            }
            _log_trade(log_entry)
            _push_completed(log_entry)
            exited.append(log_entry)
            del _open_positions[coin]
            _save_positions_now()

    return exited
