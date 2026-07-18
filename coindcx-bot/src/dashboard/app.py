import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from loguru import logger
from streamlit_autorefresh import st_autorefresh

import numpy as np

from src.config import settings, bot_config
from src.exchange.coindcx import CoinDCXExchange
from src.data.fetcher import DataFetcher
from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCIndicators
from src.indicators.volume import VolumeIndicators
from src.indicators.price_action import PriceActionIndicators
from src.strategy.scorer import TradeScorer
from src.backtest.engine import BacktestEngine
from src.data.signals_store import load_bot_signals
from src.dashboard.chatbot import render_chatbot
from src.dashboard.shared import _get_exchange, _get_db, _fetch_trades, _calc_metrics, _run_async, _get_fetcher, _fetch_all_tickers, _fetch_ohlcv


def run_dashboard():
    st.set_page_config(
        page_title="CoinDCX Pro Trading Bot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    _render_login()
    if not st.session_state.authenticated:
        return

    st.sidebar.title("🤖 CoinDCX Pro Bot")
    st.sidebar.markdown("---")

    menu = [
        "Dashboard",
        "Market Scanner",
        "Backtest",
        "Active Positions",
        "Trade History",
        "Performance",
        "Settings",
        "AI Assistant",
    ]
    choice = st.sidebar.radio("Navigation", menu)

    if choice == "Dashboard":
        _render_dashboard()
    elif choice == "Market Scanner":
        _render_scanner()
    elif choice == "Backtest":
        _render_backtest()
    elif choice == "Active Positions":
        _render_positions()
    elif choice == "Trade History":
        _render_history()
    elif choice == "Performance":
        _render_performance()
    elif choice == "Settings":
        _render_settings()
    elif choice == "AI Assistant":
        render_chatbot()

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Bot Status:** Running 🟢\n\n"
        f"**Mode:** {settings.bot_mode.upper()}"
    )


def _render_login():
    if not st.session_state.authenticated:
        st.markdown(
            "<h1 style='text-align: center;'>🤖 CoinDCX Pro Trading Bot</h1>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            st.text_input("Username", key="login_username")
            st.text_input("Password", type="password", key="login_password")
            if st.form_submit_button("Login"):
                if (
                    st.session_state.login_username == settings.dashboard_username
                    and st.session_state.login_password == settings.dashboard_password
                ):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")


def _render_dashboard():
    st.title("📊 Trading Dashboard")

    count = st_autorefresh(interval=3000, key="dash_autorefresh")

    tickers = _run_async(_fetch_all_tickers())
    btc_key = "BTCUSDT" if "BTCUSDT" in tickers else next((k for k in tickers if "BTC" in k and "USDT" in k and "WBTC" not in k), "")
    eth_key = "ETHUSDT" if "ETHUSDT" in tickers else next((k for k in tickers if "ETH" in k and "USDT" in k and "WETH" not in k), "")
    btc = tickers.get(btc_key, {})
    eth = tickers.get(eth_key, {})

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        btc_price = btc.get("last", 0)
        btc_chg = btc.get("percentage", 0)
        st.metric(
            "BTC/USDT",
            f"${btc_price:,.2f}",
            f"{btc_chg:+.2f}%" if btc_price else "N/A",
        )
    with col2:
        eth_price = eth.get("last", 0)
        eth_chg = eth.get("percentage", 0)
        st.metric(
            "ETH/USDT",
            f"${eth_price:,.2f}",
            f"{eth_chg:+.2f}%" if eth_price else "N/A",
        )
    with col3:
        total_markets = len(tickers)
        st.metric("Markets", f"{total_markets}")
    with col4:
        usdt_pairs = sum(1 for s in tickers if s.endswith("USDT"))
        st.metric("USDT Pairs", f"{usdt_pairs}")

    st.subheader("📈 Top 10 Markets by Volume")
    df_tickers = pd.DataFrame([
        {"Symbol": s, "Price": t.get("last", 0), "Volume": t.get("volume", 0),
         "Change": t.get("percentage", 0)}
        for s, t in tickers.items()
    ]).sort_values("Volume", ascending=False).head(10)
    df_tickers["Price"] = df_tickers["Price"].apply(lambda x: f"${x:,.4f}")
    df_tickers["Volume"] = df_tickers["Volume"].apply(lambda x: f"{x:,.2f}")
    df_tickers["Change"] = df_tickers["Change"].apply(lambda x: f"{x:+.2f}%")
    st.dataframe(df_tickers, use_container_width=True, hide_index=True)

    trades = _fetch_trades(limit=200)
    metrics = _calc_metrics(trades)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", metrics.get("total_trades", 0))
    col2.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")
    col3.metric("Total P&L", f"${metrics.get('total_pnl', 0):,.2f}")
    col4.metric("Open Positions", len(_fetch_trades(status="open")))

    with st.expander("📈 Equity Curve", expanded=True):
        fig = go.Figure()
        eq = metrics.get("equity_curve", [10000])
        fig.add_trace(go.Scatter(
            y=eq, mode="lines", name="Equity", line=dict(color="#00ff88", width=2),
            fill="tozeroy", fillcolor="rgba(0,255,136,0.1)",
        ))
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)


def _get_tf_hours():
    tf = bot_config.get("timeframes", {}).get("primary", "4h")
    tf_map = {"1m": 1/60, "5m": 1/12, "15m": 0.25, "30m": 0.5,
              "1h": 1, "2h": 2, "4h": 4, "6h": 6, "8h": 8, "12h": 12,
              "1d": 24, "3d": 72, "1w": 168}
    return tf_map.get(tf, 4)


async def _scan_markets(ex, max_coins, symbols=None):
    if ex is None:
        ex = CoinDCXExchange()
    tech = TechnicalIndicators()
    smc = SMCIndicators()
    vol_ind = VolumeIndicators()
    pa = PriceActionIndicators()
    risk_cfg = bot_config["risk"]
    sl_mult = risk_cfg["stop_loss_atr_multiplier"]
    tp_levels = risk_cfg["take_profit_levels"]
    tf_hours = _get_tf_hours()
    now_ts = datetime.now(timezone.utc)
    results = []

    if symbols:
        tickers = await ex.fetch_all_tickers()
        pairs = [(s, tickers.get(s, {})) for s in symbols if s in tickers]
    else:
        tickers = await ex.fetch_all_tickers()
        usdt_tickers = {s: t for s, t in tickers.items()
                        if s.endswith("USDT") and t.get("volume", 0) > 0}
        pairs = sorted(usdt_tickers.items(), key=lambda x: x[1]["volume"], reverse=True)[:max_coins]

    sem = asyncio.Semaphore(15)
    async def _fetch_one(s):
        async with sem:
            return await asyncio.wait_for(ex.fetch_ohlcv(s, f"{tf_hours}h", 50), timeout=10)
    try:
        all_ohlcv = await asyncio.wait_for(
            asyncio.gather(*[_fetch_one(s) for s, _ in pairs]),
            timeout=120,
        )
    except asyncio.TimeoutError:
        logger.warning(f"Market scan timed out after 120s ({len(pairs)} pairs)")
        return results

    for i, ((symbol, ticker), ohlcv) in enumerate(zip(pairs, all_ohlcv)):
        try:
            if ohlcv is None or len(ohlcv) < 50:
                continue

            df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)

            df = tech.compute_all(df)
            df = smc.compute_all(df)
            df = vol_ind.compute_all(df)
            df = pa.compute_all(df)

            last = df.iloc[-1]
            close = last.get("close", 0)
            rsi = last.get("rsi", 50)
            macd_dir = last.get("macd_signal_line", "neutral")
            st_dir = last.get("st_direction", "neutral")
            adx = last.get("adx", 0)
            atr = last.get("atr", 0)
            bos = last.get("bos", "none")
            choch = last.get("choch", "none")

            score = 0
            if st_dir == "uptrend":
                score += 2
            elif st_dir == "downtrend":
                score -= 2
            if macd_dir == "bullish":
                score += 2
            elif macd_dir == "bearish":
                score -= 2
            if rsi > 50:
                score += 1
            elif rsi < 50:
                score -= 1
            if adx > 25:
                score += 1 if st_dir == "uptrend" else -1 if st_dir == "downtrend" else 0
            if bos == "bullish_bos":
                score += 2
            elif bos == "bearish_bos":
                score -= 2
            if choch == "bullish_choch":
                score += 2
            elif choch == "bearish_choch":
                score -= 2

            signal = "LONG" if score >= 3 else "SHORT" if score <= -3 else "NEUTRAL"
            conf = min(abs(score) * 15 + 50, 98)

            calc_dir = signal if signal != "NEUTRAL" else ("LONG" if score >= 0 else "SHORT")
            sl = tp1 = tp2 = tp3 = None
            if calc_dir == "LONG":
                sl = close - (atr * sl_mult) if atr > 0 else close * 0.95
                for lv in tp_levels:
                    p = close + (abs(close - sl) * lv["ratio"])
                    if lv["level"] == 1: tp1 = p
                    elif lv["level"] == 2: tp2 = p
                    elif lv["level"] == 3: tp3 = p
            elif calc_dir == "SHORT":
                sl = close + (atr * sl_mult) if atr > 0 else close * 1.05
                for lv in tp_levels:
                    p = close - (abs(close - sl) * lv["ratio"])
                    if lv["level"] == 1: tp1 = p
                    elif lv["level"] == 2: tp2 = p
                    elif lv["level"] == 3: tp3 = p

            candle_time = df.index[-1]
            next_candle = candle_time + pd.Timedelta(hours=tf_hours)
            expiry_ts = int(next_candle.timestamp())

            results.append({
                "symbol": symbol,
                "signal": signal,
                "confidence": conf,
                "entry_price": close,
                "current_price": ticker.get("last", close),
                "sl_price": sl,
                "tp1_price": tp1,
                "tp2_price": tp2,
                "tp3_price": tp3,
                "trend": st_dir,
                "rsi": rsi,
                "macd_dir": macd_dir,
                "adx": adx,
                "bos": bos,
                "choch": choch,
                "expiry_ts": expiry_ts,
                "scanned_at": int(now_ts.timestamp()),
            })
        except Exception as e:
            logger.debug(f"Scan failed for {symbol}: {e}")
    return results


@st.cache_data(ttl=300)
def _cached_scan(max_coins: int):
    async def _run():
        ex = _get_exchange()
        return await _scan_markets(ex, max_coins)
    return asyncio.run(_run())


def _init_scanner_state():
    if "scanner_signals" not in st.session_state:
        st.session_state.scanner_signals = []
    if "expired_signals" not in st.session_state:
        st.session_state.expired_signals = []
    if "last_full_scan" not in st.session_state:
        st.session_state.last_full_scan = 0
    if "auto_refresh_on" not in st.session_state:
        st.session_state.auto_refresh_on = True


def _format_signal_row(s, live_price=None, is_stale=False):
    coin = s["symbol"].replace("_", "/")
    sig = s["signal"]
    sig_icon = "🟢" if sig == "LONG" else "🔴" if sig == "SHORT" else "⚪"
    trend_icon = "🟢" if s["trend"] == "uptrend" else "🔴" if s["trend"] == "downtrend" else "⚪"
    macd_icon = "🟢" if s["macd_dir"] == "bullish" else "🔴" if s["macd_dir"] == "bearish" else "⚪"
    bos_icon = "🟢" if s["bos"] == "bullish_bos" else "🔴" if s["bos"] == "bearish_bos" else "—"
    choch_icon = "🟢" if s["choch"] == "bullish_choch" else "🔴" if s["choch"] == "bearish_choch" else "—"
    current = live_price if live_price else s.get("current_price", s["entry_price"])
    pnl_pct = ((current - s["entry_price"]) / s["entry_price"] * 100) if s["entry_price"] else 0
    pnl_color = "#00ff88" if pnl_pct >= 0 else "#ff4444"
    stale_attr = ' data-stale="1"' if is_stale else ""

    def price_str(p):
        return f"${p:,.4f}" if p else "—"

    return f"""<tr{stale_attr}>
        <td><b>{coin}</b></td>
        <td style="color:{'#00ff88' if sig=='LONG' else '#ff4444' if sig=='SHORT' else '#888'}">{sig_icon} {sig}</td>
        <td>{s['confidence']:.0f}%</td>
        <td>{price_str(s['entry_price'])}</td>
        <td><span style="color:{pnl_color}">{price_str(current)}</span></td>
        <td style="color:{pnl_color}">{pnl_pct:+.2f}%</td>
        <td style="color:#ff6666">{price_str(s['sl_price'])}</td>
        <td style="color:#66ff66">{price_str(s['tp1_price'])}</td>
        <td style="color:#66ff66">{price_str(s['tp2_price'])}</td>
        <td style="color:#66ff66">{price_str(s['tp3_price'])}</td>
        <td>{trend_icon}</td>
        <td>{s['rsi']:.1f}</td>
        <td>{macd_icon}</td>
        <td>{s['adx']:.1f}</td>
        <td>{bos_icon}</td>
        <td>{choch_icon}</td>
        <td><span class="countdown" data-expiry="{s['expiry_ts']}">--</span></td>
    </tr>"""


def _render_signal_table(signals, tickers=None, now_ts=None):
    if not signals:
        return

    if now_ts is None:
        now_ts = int(datetime.now(timezone.utc).timestamp())

    def _live(sym):
        if tickers:
            t = tickers.get(sym, {})
            return t.get("last", None)
        return None

    rows = "\n".join(
        _format_signal_row(s, _live(s["symbol"]), is_stale=now_ts >= s["expiry_ts"])
        for s in signals
    )
    html = f"""<div>
    <style>
        .signal-table {{ width:100%; border-collapse:collapse; font-size:13px; color:#fff; }}
        .signal-table th {{ background:#1a1a2e; padding:8px; text-align:left; border-bottom:2px solid #333; }}
        .signal-table td {{ padding:6px 8px; border-bottom:1px solid #222; }}
        .signal-table tr:hover {{ background:#1a1a3e; }}
        .signal-table tr[data-stale="1"] {{ opacity:0.6; }}
        .signal-table tr[data-stale="1"] td {{ border-bottom:1px dashed #444; }}
        .countdown {{ font-family:monospace; font-weight:bold; color:#ffcc00; }}
        .expired-countdown {{ color:#ff4444; }}
        .stale-countdown {{ color:#ff8800 !important; }}
    </style>
    <table class="signal-table">
        <thead><tr>
            <th>Coin</th><th>Signal</th><th>Conf</th><th>Entry</th><th>Current</th><th>Chg%</th><th>SL</th><th>TP1</th><th>TP2</th><th>TP3</th>
            <th>Trend</th><th>RSI</th><th>MACD</th><th>ADX</th><th>BOS</th><th>CHOCH</th><th>Validity</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>
    <script>
    (function() {{
        function updateAll() {{
            document.querySelectorAll('.countdown').forEach(function(el) {{
                var expiry = parseInt(el.getAttribute('data-expiry')) * 1000;
                var diff = expiry - Date.now();
                var tr = el.closest('tr');
                if (diff <= 0) {{
                    el.innerHTML = '⚠️ STALE';
                    el.className = 'countdown stale-countdown';
                    if (tr) tr.setAttribute('data-stale', '1');
                }} else {{
                    var h = Math.floor(diff / 3600000);
                    var m = Math.floor((diff % 3600000) / 60000);
                    var s = Math.floor((diff % 60000) / 1000);
                    el.innerHTML = h + 'h ' + String(m).padStart(2,'0') + 'm ' + String(s).padStart(2,'0') + 's';
                    if (tr) tr.removeAttribute('data-stale');
                }}
            }});
        }}
        updateAll();
        setInterval(updateAll, 1000);
    }})();
    </script>
    </div>"""
    st.components.v1.html(html, height=len(signals) * 36 + 120, scrolling=True)


def _calc_pnl(signal, price_at_expiry):
    if price_at_expiry is None or signal["entry_price"] is None or signal["entry_price"] == 0:
        return 0
    if signal["signal"] == "LONG":
        return (price_at_expiry - signal["entry_price"]) / signal["entry_price"] * 100
    elif signal["signal"] == "SHORT":
        return (signal["entry_price"] - price_at_expiry) / signal["entry_price"] * 100
    return 0


def _render_expired_signals():
    if not st.session_state.expired_signals:
        return

    with st.expander(f"📜 Expired Signals ({len(st.session_state.expired_signals)})", expanded=False):
        for ex_sig in reversed(st.session_state.expired_signals[-50:]):
            pnl = ex_sig.get("pnl_percent", 0)
            pnl_color = "#00ff88" if pnl >= 0 else "#ff4444"
            pnl_icon = "🟢" if pnl >= 0 else "🔴"
            entry = ex_sig.get("entry_price", 0)
            expiry_price = ex_sig.get("price_at_expiry", 0)
            scanned = datetime.fromtimestamp(ex_sig.get("scanned_at", 0), tz=timezone.utc).strftime("%H:%M")
            expired = datetime.fromtimestamp(ex_sig.get("expired_at", 0), tz=timezone.utc).strftime("%H:%M")

            col1, col2, col3, col4, col5 = st.columns([1.2, 0.8, 1.2, 1, 1.2])
            with col1:
                st.markdown(f"**{ex_sig['symbol'].replace('_', '/')}**")
                st.caption(f"Scanned {scanned} → Expired {expired}")
            with col2:
                sig = ex_sig["signal"]
                st.markdown(f"{'🟢' if sig=='LONG' else '🔴'} **{sig}**")
            with col3:
                st.markdown(f"Entry: **${entry:,.4f}**")
                st.caption(f"Expiry: ${expiry_price:,.4f}" if expiry_price else "N/A")
            with col4:
                st.markdown(f"<span style='color:{pnl_color};font-size:1.3em;font-weight:bold'>{pnl_icon} {pnl:+.2f}%</span>", unsafe_allow_html=True)
                sl_pnl = ex_sig.get("sl_pnl_percent", 0)
                if sl_pnl != 0:
                    st.caption(f"SL would hit: {sl_pnl:+.2f}%")
            with col5:
                if ex_sig.get("tp1_price"):
                    st.caption(f"TP1: ${ex_sig['tp1_price']:,.4f}")
                if ex_sig.get("tp2_price"):
                    st.caption(f"TP2: ${ex_sig['tp2_price']:,.4f}")
                if ex_sig.get("tp3_price"):
                    st.caption(f"TP3: ${ex_sig['tp3_price']:,.4f}")
            st.divider()


def _render_scanner():
    st.title("🔍 Market Scanner")
    _init_scanner_state()

    refresh_count = 0
    if st.session_state.auto_refresh_on:
        refresh_count = st_autorefresh(interval=5000, key="scanner_autorefresh")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        scan_type = st.radio("Scan Type", ["Quick Scan (Top 30)", "Full Scan (All USDT pairs)"], horizontal=True, label_visibility="collapsed")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=st.session_state.auto_refresh_on)
        if auto_refresh != st.session_state.auto_refresh_on:
            st.session_state.auto_refresh_on = auto_refresh
            st.rerun()
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        run_scan = st.button("🚀 Scan Now", type="primary", use_container_width=True)

    max_coins = 30 if "Quick" in scan_type else 100
    now_ts = int(datetime.now(timezone.utc).timestamp())

    bot_signals = load_bot_signals()
    if bot_signals:
        st.session_state.scanner_signals = bot_signals
        st.session_state.last_full_scan = now_ts

    scan_interval = 120
    should_scan = (
        run_scan
        or (st.session_state.auto_refresh_on and st.session_state.last_full_scan == 0)
        or (st.session_state.auto_refresh_on and (now_ts - st.session_state.last_full_scan) > scan_interval)
    )

    if not st.session_state.scanner_signals and st.session_state.auto_refresh_on and st.session_state.last_full_scan == 0:
        st.info(f"⏳ Waiting for bot scan... signals will appear once the bot completes its analysis cycle")

    if should_scan and not bot_signals:
        new_signals = _cached_scan(max_coins)
        if new_signals:
            st.session_state.scanner_signals = new_signals
        st.session_state.last_full_scan = now_ts

    stale_count = sum(1 for s in st.session_state.scanner_signals if now_ts >= s["expiry_ts"])
    from_bot = any(s.get("from_bot") for s in st.session_state.scanner_signals)

    if st.session_state.scanner_signals:
        long_count = sum(1 for s in st.session_state.scanner_signals if s["signal"] == "LONG")
        short_count = sum(1 for s in st.session_state.scanner_signals if s["signal"] == "SHORT")
        neutral_count = sum(1 for s in st.session_state.scanner_signals if s["signal"] == "NEUTRAL")

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Signals", len(st.session_state.scanner_signals))
        col2.metric("🟢 LONG", long_count)
        col3.metric("🔴 SHORT", short_count)
        col4.metric("⚪ Neutral", neutral_count)
        col5.metric("⚠️ Stale", stale_count)

        if from_bot:
            st.caption("🤖 Signals from bot's strategy engine")

        live_tickers = {}
        try:
            ticker_data = _run_async(_fetch_all_tickers())
            if ticker_data:
                live_tickers = ticker_data
        except Exception:
            pass
        _render_signal_table(st.session_state.scanner_signals, tickers=live_tickers, now_ts=now_ts)

        st.download_button(
            "📥 Download CSV",
            pd.DataFrame(st.session_state.scanner_signals).to_csv(index=False),
            "market_scan.csv", "text/csv",
        )

        if stale_count > 0:
            st.caption(f"⚠️ {stale_count} signal(s) are stale. Click **Scan Now** to refresh.")
    elif not run_scan:
        st.info("No active signals. Waiting for bot scan or click **🚀 Scan Now** for manual scan.")

    _render_expired_signals()

    if st.session_state.expired_signals and st.button("🗑️ Clear Expired History", type="secondary"):
        st.session_state.expired_signals = []
        st.rerun()


def _render_backtest():
    st.title("📊 Backtesting")
    st.markdown("Run strategy backtests on real historical data from CoinDCX.")

    col1, col2 = st.columns(2)
    with col1:
        symbol = st.selectbox(
            "Symbol",
            ["BTC_USDT", "ETH_USDT", "SOL_USDT", "BNB_USDT", "XRP_USDT", "ADA_USDT", "DOGE_USDT", "DOT_USDT"],
        )
        timeframe = st.selectbox("Timeframe", ["1h", "4h", "12h", "1d"])
    with col2:
        days = st.selectbox("Period", [30, 60, 90, 180, 365], index=2, format_func=lambda d: f"{d} days")
        initial_balance = st.number_input("Initial Balance ($)", 1000, 100000, 10000, step=1000)

    if st.button("▶️ Run Backtest", type="primary"):
        tf_limit = {1: 500, 4: 300, 12: 200, 24: 200}
        limit = min(tf_limit.get({"1h": 1, "4h": 4, "12h": 12, "1d": 24}.get(timeframe, 4), 300) * days, 500)

        with st.spinner(f"Fetching {days} days of {timeframe} data for {symbol}..."):
            ohlcv = _run_async(_fetch_ohlcv(symbol, timeframe, limit))

        if len(ohlcv) < 100:
            st.error(f"Not enough data ({len(ohlcv)} candles). Need at least 100.")
            return

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)

        with st.spinner("Running backtest engine..."):
            engine = BacktestEngine(initial_balance=initial_balance)
            result = _run_async(engine.run(df, symbol=symbol))

        if "error" in result:
            st.error(result["error"])
            return

        st.success("Backtest complete!")
        _render_backtest_results(result, df, engine, initial_balance)


def _render_backtest_results(result: dict, df: pd.DataFrame, engine, initial_balance=10000):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", result.get("total_trades", 0))
    col2.metric("Win Rate", f"{result.get('win_rate', 0):.1f}%")
    col3.metric("Profit Factor", f"{result.get('profit_factor', 0):.2f}")
    col4.metric("Sharpe Ratio", f"{result.get('sharpe_ratio', 0):.2f}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Max Drawdown", f"{result.get('max_drawdown', 0):.2f}%")
    col2.metric("Net Profit", f"${result.get('net_profit', 0):,.2f}")
    col3.metric("Total Return", f"{result.get('total_return', 0):.2f}%")
    col4.metric("Avg Trade", f"${result.get('average_trade', 0):,.2f}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Sortino Ratio", f"{result.get('sortino_ratio', 0):.2f}")
    col2.metric("Expectancy", f"${result.get('expectancy', 0):,.2f}")
    col3.metric("Recovery Factor", f"{result.get('recovery_factor', 0):.2f}")

    with st.expander("📈 Equity Curve", expanded=True):
        fig = go.Figure()
        eq = engine.equity_curve if engine.equity_curve else [initial_balance]
        fig.add_trace(go.Scatter(
            y=eq, mode="lines", name="Equity",
            line=dict(color="#00ff88", width=2),
            fill="tozeroy", fillcolor="rgba(0,255,136,0.1)",
        ))
        fig.update_layout(
            template="plotly_dark", height=400,
            title="Equity Curve",
            xaxis_title="Trade #", yaxis_title="Balance ($)",
        )
        st.plotly_chart(fig, use_container_width=True)

    if engine.trades:
        with st.expander("📋 Trade List", expanded=False):
            trades_df = pd.DataFrame(engine.trades)
            cols = ["symbol", "side", "entry_price", "exit_price", "pnl", "pnl_percent", "reason_exit"]
            trades_df = trades_df[[c for c in cols if c in trades_df.columns]]
            trades_df["pnl"] = trades_df["pnl"].apply(lambda x: f"${x:+.2f}")
            trades_df["pnl_percent"] = trades_df["pnl_percent"].apply(lambda x: f"{x:+.2f}%")
            st.dataframe(trades_df, use_container_width=True, hide_index=True)


def _render_positions():
    st.title("📋 Active Positions")
    st_autorefresh(interval=1000, key="pos_autorefresh")
    open_trades = _fetch_trades(status="open")
    if not open_trades:
        st.info("No active positions.")
        return

    tickers = _run_async(_fetch_all_tickers())
    rows = []
    for t in open_trades:
        sym = t.symbol.replace("_", "/")
        side = t.side.upper()
        entry = t.entry_price or 0
        lev = t.leverage or 1
        ticker = tickers.get(t.symbol, {})
        current = ticker.get("last", entry)
        if side == "LONG":
            pnl_pct = ((current - entry) / entry * 100) if entry else 0
        else:
            pnl_pct = ((entry - current) / entry * 100) if entry else 0
        sl = t.stop_loss or 0
        tp = t.take_profit_1 or 0
        rows.append({
            "Symbol": sym, "Side": side, "Entry": f"${entry:,.4f}",
            "Current": f"${current:,.4f}",
            "PnL": f"{pnl_pct:+.2f}%",
            "SL": f"${sl:,.4f}" if sl else "—",
            "TP": f"${tp:,.4f}" if tp else "—",
            "Qty": t.quantity,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_history():
    st.title("📜 Trade History")
    all_trades = _fetch_trades(limit=500)
    if not all_trades:
        st.info("No trade history yet.")
        return

    rows = []
    for t in all_trades:
        rows.append({
            "ID": t.id, "Symbol": t.symbol.replace("_", "/"),
            "Side": t.side.upper(), "Entry": f"${t.entry_price:,.4f}" if t.entry_price else "—",
            "Exit": f"${t.exit_price:,.4f}" if t.exit_price else "—",
            "PnL": f"${t.pnl:+,.2f} ({t.pnl_percent:+.2f}%)" if t.pnl is not None and t.pnl_percent is not None else ("—" if t.pnl is None else f"${t.pnl:+,.2f}"),
            "Status": t.status.upper(),
            "Reason": t.reason_exit or "—",
            "Time": t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else "—",
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    closed = [t for t in all_trades if t.status == "closed"]
    if closed:
        wins = sum(1 for t in closed if t.pnl is not None and t.pnl > 0)
        losses = sum(1 for t in closed if t.pnl is not None and t.pnl < 0)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Closed", len(closed))
        col2.metric("Wins", wins)
        col3.metric("Losses", losses)


def _render_performance():
    st.title("📈 Performance Metrics")
    trades = _fetch_trades(limit=500)
    m = _calc_metrics(trades)
    if not m:
        st.info("No trade data yet. Run the bot and execute trades to see performance.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Win Rate", f"{m['win_rate']:.1f}%", f"{m['winning_trades']}/{m['losing_trades']}" if m['total_trades'] else None)
    col2.metric("Profit Factor", f"{m['profit_factor']:.2f}")
    col3.metric("Sharpe Ratio", f"{m['sharpe_ratio']:.2f}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Sortino Ratio", f"{m['sortino_ratio']:.2f}")
    col2.metric("Max Drawdown", f"{m['max_drawdown']:.2f}%")
    col3.metric("Expectancy", f"${m['expectancy']:.2f}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", m['total_trades'])
    col2.metric("Total P&L", f"${m['total_pnl']:+,.2f}")
    col3.metric("Avg Trade", f"${m['average_trade']:+,.2f}")

    if m.get("equity_curve"):
        with st.expander("📈 Equity Curve", expanded=True):
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=m["equity_curve"], mode="lines", name="Equity",
                line=dict(color="#00ff88", width=2),
                fill="tozeroy", fillcolor="rgba(0,255,136,0.1)",
            ))
            fig.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig, use_container_width=True)


def _render_settings():
    import json
    from pathlib import Path
    from src.config import reload_config

    st.title("⚙️ Settings")
    bc = bot_config
    with st.form("settings_form"):
        st.subheader("Bot Configuration")
        col1, col2 = st.columns(2)
        with col1:
            mode = st.selectbox("Mode", ["Paper", "Live"], index=0 if bc["bot"]["mode"] == "paper" else 1)
            max_pos = st.number_input("Max Positions", 1, 10, bc["bot"]["max_positions"])
            risk_pct = st.number_input("Max Risk Per Trade (%)", 0.1, 5.0, bc["risk"]["max_risk_per_trade"])
            min_conf = st.number_input("Min Confidence (%)", 50, 100, bc["bot"]["min_confidence"])
        with col2:
            min_rr = st.number_input("Min Risk/Reward", 1.0, 10.0, bc["bot"]["min_rr"])
            max_dd = st.number_input("Max Drawdown (%)", 5.0, 50.0, bc["risk"]["max_drawdown"])
            max_losses = st.number_input("Max Consecutive Losses", 1, 10, bc["risk"]["max_consecutive_losses"])
            leverage = st.number_input("Leverage", 1, 10, bc["bot"]["leverage"])

        saved = st.form_submit_button("Save Settings")
        if saved:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
            with open(config_path) as f:
                cfg = json.load(f)
            cfg["bot"]["mode"] = mode.lower()
            cfg["bot"]["max_positions"] = int(max_pos)
            cfg["risk"]["max_risk_per_trade"] = risk_pct
            cfg["bot"]["min_confidence"] = int(min_conf)
            cfg["bot"]["min_rr"] = min_rr
            cfg["risk"]["max_drawdown"] = max_dd
            cfg["risk"]["max_consecutive_losses"] = int(max_losses)
            cfg["bot"]["leverage"] = int(leverage)
            with open(config_path, "w") as f:
                json.dump(cfg, f, indent=2)
            reload_config()
            st.success("Settings saved! Bot will use new values on next cycle.")


if __name__ == "__main__":
    run_dashboard()
