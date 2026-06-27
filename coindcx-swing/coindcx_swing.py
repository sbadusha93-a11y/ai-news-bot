import sys
import os
import time
import traceback
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.table import Table
from rich import box

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import data_fetcher as df
import indicators as ind
import scorer_swing as sc
import numpy as np
from display_swing import LiveDisplay
import dashboard_swing
import fundamentals as fund

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
console = Console()


def time_to_candle_close(interval_minutes):
    now = datetime.now(timezone.utc)
    total_mins = now.hour * 60 + now.minute
    current_block = (total_mins // interval_minutes) * interval_minutes
    next_block = current_block + interval_minutes
    if next_block >= 1440:
        next_dt = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        h = int(next_block // 60)
        m = int(next_block % 60)
        next_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
    secs = max(0, (next_dt - now).total_seconds())
    if interval_minutes >= 60:
        hh = int(secs // 3600)
        mm = int((secs % 3600) // 60)
        ss = int(secs % 60)
        return f"{hh}:{mm:02d}:{ss:02d}", int(secs)
    else:
        mm = int(secs // 60)
        ss = int(secs % 60)
        return f"{mm}:{ss:02d}", int(secs)


def suggest_leverage(atr_val, price):
    if price <= 0 or atr_val <= 0:
        return "3x"
    atr_pct = (atr_val / price) * 100
    if atr_pct > 3.0:
        return "2x"
    elif atr_pct > 1.5:
        return "3x"
    elif atr_pct > 0.8:
        return "5x"
    else:
        return "5x"


def calc_pnl(entry, current, direction):
    if not entry or entry == 0:
        return None
    if direction == "LONG":
        return ((current - entry) / entry) * 100
    elif direction == "SHORT":
        return ((entry - current) / entry) * 100
    return None


def compute_1h_indicators(closes, highs, lows, volumes):
    if len(closes) < 200:
        return None
    ema20_arr = ind.ema(closes, 20)
    ema50_arr = ind.ema(closes, 50)
    ema200_arr = ind.ema(closes, 200)
    vwap_arr = ind.vwap(highs, lows, closes, volumes)
    rsi_arr = ind.rsi(closes, 14)
    macd_line, sig_line, macd_hist = ind.macd(closes)
    sk_arr, sd_arr = ind.stoch_rsi(closes)
    atr_arr = ind.atr(highs, lows, closes)
    high_10_arr = ind.highest(highs, 10)
    low_10_arr = ind.lowest(lows, 10)
    return {
        "ema20": ema20_arr,
        "ema50": ema50_arr,
        "ema200": ema200_arr,
        "vwap": vwap_arr,
        "rsi": rsi_arr,
        "macd_line": macd_line,
        "sig_line": sig_line,
        "macd_hist": macd_hist,
        "sk": sk_arr,
        "sd": sd_arr,
        "atr": atr_arr,
        "high_10": high_10_arr,
        "low_10": low_10_arr,
    }


def extract_candle_arrays(candle_data):
    candles = candle_data[::-1]
    closes = np.array([float(c["close"]) for c in candles], dtype=float)
    highs = np.array([float(c["high"]) for c in candles], dtype=float)
    lows = np.array([float(c["low"]) for c in candles], dtype=float)
    volumes = np.array([float(c["volume"]) for c in candles], dtype=float)
    return candles, closes, highs, lows, volumes


def get_btc_trend(interval="1h", limit=500):
    try:
        btc_candles = df.fetch_btc_candles(interval, limit)
        if not btc_candles or len(btc_candles) < 200:
            return "neutral"
        _, btc_closes, btc_highs, btc_lows, btc_volumes = extract_candle_arrays(btc_candles)
        if len(btc_closes) < 200:
            return "neutral"
        btc_ema20 = ind.ema(btc_closes, 20)[-1]
        btc_ema50 = ind.ema(btc_closes, 50)[-1]
        btc_vwap = ind.vwap(btc_highs, btc_lows, btc_closes, btc_volumes)[-1]
        btc_price = btc_closes[-1]
        if btc_price > btc_vwap and btc_ema20 > btc_ema50:
            return "bullish"
        elif btc_price < btc_vwap and btc_ema20 < btc_ema50:
            return "bearish"
        else:
            return "neutral"
    except Exception:
        return "neutral"


def analyze_coin(candle_data, coin_name, current_positions, btc_trend, fund_data=None):
    try:
        if not candle_data or len(candle_data) < 200:
            return None

        candles, closes, highs, lows, volumes = extract_candle_arrays(candle_data)
        latest = candles[-1]
        price = float(latest["close"])
        candle_time = float(latest["time"]) / 1000
        age_hours = (time.time() - candle_time) / 3600
        if age_hours > 5:
            return None

        indicators = compute_1h_indicators(closes, highs, lows, volumes)
        if indicators is None:
            return None

        ema20 = indicators["ema20"][-1]
        ema50 = indicators["ema50"][-1]
        ema200 = indicators["ema200"][-1]
        vwap = indicators["vwap"][-1]
        rsi_val = indicators["rsi"][-1]
        macd_line = indicators["macd_line"][-1]
        sig_line = indicators["sig_line"][-1]
        macd_hist = indicators["macd_hist"][-1]
        sk = indicators["sk"][-1]
        sd = indicators["sd"][-1]
        sk_prev = indicators["sk"][-2]
        sd_prev = indicators["sd"][-2]
        atr_val = indicators["atr"][-1]
        high_10 = indicators["high_10"][-1]
        low_10 = indicators["low_10"][-1]

        curr_candle = candles[-1]
        prev_candle = candles[-2]
        patterns = ind.detect_candle_pattern(
            float(curr_candle["open"]),
            float(curr_candle["high"]),
            float(curr_candle["low"]),
            float(curr_candle["close"]),
            float(prev_candle["open"]),
            float(prev_candle["high"]),
            float(prev_candle["low"]),
            float(prev_candle["close"]),
        )

        signal, direction, checks, long_pct, short_pct = sc.get_signal(
            price, vwap, ema20, ema50, ema200, rsi_val,
            macd_line, sig_line, macd_hist,
            sk, sd, sk_prev, sd_prev,
            patterns, btc_trend,
        )

        pos_key = coin_name
        prev_pos = current_positions.get(pos_key)
        pos_direction = prev_pos["direction"] if prev_pos else None
        pos_entry = prev_pos["entry"] if prev_pos else None
        pos_target = prev_pos["target"] if prev_pos else None
        pos_sl = prev_pos["sl"] if prev_pos else None

        exit_reasons = []
        pnl_val = None
        entry = None
        target = None
        sl = None
        tp1 = None
        tp2 = None
        rr = None
        entry_display = None

        if direction in ("LONG", "SHORT"):
            entry = sc.calculate_entry(
                float(latest["high"]), float(latest["low"]), price,
                high_10, low_10, direction,
            )
            target, sl, rr, tp1, tp2 = sc.calculate_target_sl(entry, atr_val, high_10, low_10, direction)
            entry_display = entry

            if pos_key not in current_positions:
                current_positions[pos_key] = {
                    "entry": entry,
                    "target": target,
                    "sl": sl,
                    "direction": direction,
                }

        if pos_direction and prev_pos:
            if pos_direction == "LONG":
                exit_reasons = sc.check_long_exit(
                    price, ema20, rsi_val, macd_line, sig_line,
                    pos_entry, pos_target, pos_sl,
                )
            elif pos_direction == "SHORT":
                exit_reasons = sc.check_short_exit(
                    price, ema20, rsi_val, macd_line, sig_line,
                    pos_entry, pos_target, pos_sl,
                )

            if not exit_reasons and direction != pos_direction:
                exit_reasons = [f"Signal->{direction}"]

            if exit_reasons:
                pnl_val = calc_pnl(pos_entry, price, pos_direction)
                if pnl_val is not None:
                    is_win = 1 if pnl_val > 0 else 0
                    is_loss = 1 if pnl_val <= 0 else 0
                    current_positions[f"success_{coin_name}"] = current_positions.get(f"success_{coin_name}", 0) + is_win
                    current_positions[f"failed_{coin_name}"] = current_positions.get(f"failed_{coin_name}", 0) + is_loss
                del current_positions[pos_key]

        leverage = suggest_leverage(atr_val, price) if atr_val else "3x"
        success_count = current_positions.get(f"success_{coin_name}", 0)
        failed_count = current_positions.get(f"failed_{coin_name}", 0)
        total_trades = success_count + failed_count
        win_rate = round(success_count / total_trades * 100, 1) if total_trades > 0 else 0

        fund_score_raw, fund_checks = fund.score_fundamentals(fund_data, price) if fund_data else (0, {})
        fund_score = round(min(fund_score_raw / 6 * 100, 100), 1)

        tech_score = max(long_pct or 0, short_pct or 0)
        rsi_quality = 0
        if rsi_val is not None:
            if direction == "LONG":
                rsi_quality = min(max((rsi_val - 50) / 30 * 100, 0), 100)
            elif direction == "SHORT":
                rsi_quality = min(max((50 - rsi_val) / 30 * 100, 0), 100)
            else:
                rsi_quality = min(max(100 - abs(rsi_val - 50) * 4, 0), 100)
        trend_score = 100 if (direction == "LONG" and btc_trend == "bullish") or (direction == "SHORT" and btc_trend == "bearish") else 50 if btc_trend == "neutral" else 0

        model_score = round(
            tech_score * 0.35 +
            fund_score * 0.25 +
            rsi_quality * 0.20 +
            trend_score * 0.10 +
            50 * 0.10,
            1
        )
        model_score = min(model_score, 100)

        macd_status = "POS" if macd_line > sig_line else "NEG"
        ema_order = "Y" if ema20 > ema50 > ema200 else "N"

        return {
            "coin": coin_name,
            "price": price,
            "direction": direction,
            "entry": entry_display,
            "target": target,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "rr": rr or 0,
            "leverage": leverage,
            "checks": checks,
            "long_pct": long_pct,
            "short_pct": short_pct,
            "exit_reasons": exit_reasons,
            "pnl": pnl_val,
            "success": success_count,
            "failed": failed_count,
            "win_rate": win_rate,
            "fund_score": fund_score,
            "fund_checks": fund_checks,
            "model_score": model_score,
            "rsi": round(float(rsi_val), 1),
            "macd": macd_status,
            "ema_order": ema_order,
            "stoch_k": round(float(sk), 1),
            "stoch_d": round(float(sd), 1),
        }
    except Exception as e:
        console.print(f"[red]Error analyzing {coin_name}: {e}[/red]")
        return None


def main():
    try:
        display = LiveDisplay()
        dashboard_swing.start()
        console.print("[bold cyan]Coindcx 4H Swing Bot Started[/bold cyan]")
        console.print(f"[green]Dashboard: http://{dashboard_swing._host}:{dashboard_swing._port}/[/green]")
        console.print("Checking...")

        pairs = df.get_top_futures_pairs(25, extra_symbols=["ZEC"])
        if not pairs:
            console.print("[red]No USDT pairs found[/red]")
            return

        coin_names = [df.from_candle_pair(df.to_candle_pair(p["market"])) for p in pairs]
        console.print(f"Tracking: {', '.join(coin_names)}")

        current_positions = {}
        last_analysis_time = 0
        cooldown = 60

        while True:
            try:
                candle_str, secs_left = time_to_candle_close(240)
                now = time.time()

                btc_trend = get_btc_trend("4h", 300)

                if now - last_analysis_time >= cooldown:
                    last_analysis_time = now
                    candles_map = df.fetch_all_candles(pairs, "4h", 300)

                    fund_map = fund.fetch_fundamentals(coin_names)

                    rows = []
                    for p in pairs:
                        coin_name = df.from_candle_pair(df.to_candle_pair(p["market"]))
                        candle_data = candles_map.get(p["market"])
                        fund_data = fund_map.get(coin_name.lower())
                        result = analyze_coin(candle_data, coin_name, current_positions, btc_trend, fund_data)
                        if result:
                            rows.append(result)

                    display.detect_and_notify(rows)

                    table = Table(
                        title=f"[bold cyan]Coindcx 4H Swing Scanner | BTC: {btc_trend.upper()} | Next: {candle_str} | Pairs: {len(rows)}[/bold cyan]",
                        box=box.ASCII,
                        header_style="bold magenta",
                    )

                    table.add_column("Coin", style="cyan", no_wrap=True)
                    table.add_column("Price", justify="right", width=10)
                    table.add_column("Dir", justify="center", width=4)
                    table.add_column("Entry", justify="right", width=10)
                    table.add_column("TP", justify="right", width=10)
                    table.add_column("SL", justify="right", width=10)
                    table.add_column("R:R", justify="center", width=5)
                    table.add_column("Lev", justify="center", width=3)
                    table.add_column("L%", justify="right", width=5)
                    table.add_column("S%", justify="right", width=5)
                    table.add_column("PnL", justify="right", width=7)
                    table.add_column("S/F", justify="center", width=5)
                    table.add_column("WR%", justify="right", width=5)
                    table.add_column("Fund", justify="right", width=5)
                    table.add_column("Model", justify="right", width=6)

                    for r in rows:
                        lev_style = "green" if r["leverage"] and "5" in r["leverage"] else "yellow" if r["leverage"] and "3" in r["leverage"] else "red"

                        lp = r["long_pct"]
                        sp = r["short_pct"]
                        lp_s = f"{lp}%" if lp is not None else "-"
                        sp_s = f"{sp}%" if sp is not None else "-"

                        if lp is not None:
                            if lp >= 80:
                                lp_s = f"[green]{lp}%[/green]"
                            elif lp >= 60:
                                lp_s = f"[yellow]{lp}%[/yellow]"
                            else:
                                lp_s = f"[red]{lp}%[/red]"

                        if sp is not None:
                            if sp >= 80:
                                sp_s = f"[green]{sp}%[/green]"
                            elif sp >= 60:
                                sp_s = f"[yellow]{sp}%[/yellow]"
                            else:
                                sp_s = f"[red]{sp}%[/red]"

                        dir_style = "green" if r["direction"] == "LONG" else "red" if r["direction"] == "SHORT" else "white"
                        dir_text = r["direction"] if r["direction"] else "-"
                        entry_text = f"{r['entry']:.8f}" if r["entry"] else "-"
                        tp_text = f"{r['target']:.8f}" if r["target"] else "-"
                        sl_text = f"{r['sl']:.8f}" if r["sl"] else "-"
                        rr_text = f"{r['rr']:.2f}" if r["rr"] and r["rr"] > 0 else "-"
                        pnl_text = f"{r['pnl']:+.2f}%" if r["pnl"] is not None else "-"
                        if r["pnl"] is not None:
                            pnl_style = "green" if r["pnl"] > 0 else "red"
                            pnl_text = f"[{pnl_style}]{r['pnl']:+.2f}%[/{pnl_style}]"

                        sf_text = f"{r['success']}/{r['failed']}" if r["success"] + r["failed"] > 0 else "-"
                        wr_text = f"{r['win_rate']}%" if r["win_rate"] > 0 else "-"

                        fs = r.get("fund_score", 0)
                        fs_s = f"[green]{fs}%[/green]" if fs >= 60 else f"[yellow]{fs}%[/yellow]" if fs >= 30 else f"[red]{fs}%[/red]"
                        ms = r.get("model_score", 0)
                        ms_s = f"[green]{ms}%[/green]" if ms >= 60 else f"[yellow]{ms}%[/yellow]" if ms >= 30 else f"[red]{ms}%[/red]"

                        table.add_row(
                            r["coin"], f"{r['price']:.8f}",
                            f"[{dir_style}]{dir_text}[/{dir_style}]",
                            entry_text, tp_text, sl_text, rr_text,
                            f"[{lev_style}]{r['leverage']}[/{lev_style}]",
                            str(lp_s), str(sp_s), pnl_text, sf_text, wr_text,
                            fs_s, ms_s,
                        )

                    display.console.clear()
                    display.console.print(table)
                    dashboard_swing.update_data(rows, btc_trend, candle_str)

                remaining = max(0, cooldown - (time.time() - last_analysis_time))
                sleep_time = min(1, remaining) if remaining > 0 else 1
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                console.print("\n[yellow]Shutting down...[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error in main loop: {e}[/red]")
                traceback.print_exc()
                time.sleep(5)

    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
