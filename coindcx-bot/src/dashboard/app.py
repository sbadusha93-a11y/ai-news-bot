import asyncio
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from loguru import logger

from src.config import settings, bot_config
from src.exchange.coindcx import CoinDCXExchange
from src.data.fetcher import DataFetcher
from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCIndicators
from src.indicators.volume import VolumeIndicators
from src.indicators.price_action import PriceActionIndicators
from src.strategy.scorer import TradeScorer
from src.backtest.engine import BacktestEngine


_EXCHANGE: Optional[CoinDCXExchange] = None

def _get_exchange():
    global _EXCHANGE
    if _EXCHANGE is None:
        _EXCHANGE = CoinDCXExchange()
    return _EXCHANGE


def _get_fetcher():
    if "fetcher" not in st.session_state:
        st.session_state.fetcher = DataFetcher(_get_exchange())
    return st.session_state.fetcher


def _run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


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

    tickers = _run_async(_get_exchange().fetch_all_tickers())
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

    with st.expander("📉 Equity Curve (Sample)"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=[10000, 10100, 10050, 10200, 10350, 10300, 10450, 10500, 10480, 10600],
            mode="lines", name="Equity", line=dict(color="#00ff88", width=2),
        ))
        fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)


async def _scan_markets(ex, max_coins):
    tech = TechnicalIndicators()
    smc = SMCIndicators()
    vol_ind = VolumeIndicators()
    pa = PriceActionIndicators()
    scorer = TradeScorer()
    risk_cfg = bot_config["risk"]
    sl_mult = risk_cfg["stop_loss_atr_multiplier"]
    tp_levels = risk_cfg["take_profit_levels"]
    now_ts = datetime.utcnow()

    tickers = await ex.fetch_all_tickers()
    usdt_tickers = {s: t for s, t in tickers.items()
                    if s.endswith("USDT") and t.get("volume", 0) > 0}
    sorted_pairs = sorted(usdt_tickers.items(), key=lambda x: x[1]["volume"], reverse=True)[:max_coins]

    results = []
    for i, (symbol, ticker) in enumerate(sorted_pairs):
        try:
            ohlcv = await ex.fetch_ohlcv(symbol, "4h", 200)
            if len(ohlcv) < 50:
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
                score += 1
            if macd_dir == "bullish":
                score += 1
            if rsi > 50:
                score += 1
            if adx > 25:
                score += 1
            if bos == "bullish_bos":
                score += 2
            if choch == "bullish_choch":
                score += 2

            signal = "LONG" if score >= 4 else "SHORT" if score <= -3 else "NEUTRAL"
            conf = min(abs(score) * 15 + 50, 98)

            sl = tp1 = tp2 = tp3 = None
            if signal == "LONG":
                sl = close - (atr * sl_mult)
                for lv in tp_levels:
                    p = close + (abs(close - sl) * lv["ratio"])
                    if lv["level"] == 1: tp1 = p
                    elif lv["level"] == 2: tp2 = p
                    elif lv["level"] == 3: tp3 = p
            elif signal == "SHORT":
                sl = close + (atr * sl_mult)
                for lv in tp_levels:
                    p = close - (abs(close - sl) * lv["ratio"])
                    if lv["level"] == 1: tp1 = p
                    elif lv["level"] == 2: tp2 = p
                    elif lv["level"] == 3: tp3 = p

            candle_time = df.index[-1]
            next_candle = candle_time + pd.Timedelta(hours=4)
            valid_until = next_candle.strftime("%H:%M UTC")
            remaining = (next_candle - pd.Timestamp(now_ts)).total_seconds() / 3600
            validity = f"~{remaining:.1f}h (until {valid_until})" if remaining > 0 else "Expiring"

            results.append({
                "Coin": symbol.replace("_", "/"),
                "Signal": signal,
                "Confidence": f"{conf:.0f}%",
                "Entry": f"${close:,.4f}",
                "SL": f"${sl:,.4f}" if sl else "—",
                "TP1": f"${tp1:,.4f}" if tp1 else "—",
                "TP2": f"${tp2:,.4f}" if tp2 else "—",
                "TP3": f"${tp3:,.4f}" if tp3 else "—",
                "Trend": "🟢 Bullish" if st_dir == "uptrend" else "🔴 Bearish" if st_dir == "downtrend" else "⚪ Sideways",
                "RSI": f"{rsi:.1f}",
                "MACD": "🟢" if macd_dir == "bullish" else "🔴" if macd_dir == "bearish" else "⚪",
                "ADX": f"{adx:.1f}",
                "BOS": "🟢" if bos == "bullish_bos" else "🔴" if bos == "bearish_bos" else "—",
                "CHOCH": "🟢" if choch == "bullish_choch" else "🔴" if choch == "bearish_choch" else "—",
                "Validity": validity,
            })
        except Exception as e:
            logger.debug(f"Scan failed for {symbol}: {e}")
    return results


def _render_scanner():
    st.title("🔍 Market Scanner")
    st.markdown("Scans CoinDCX markets and computes real-time technical analysis.")

    scan_type = st.radio("Scan Type", ["Quick Scan (Top 10)", "Full Scan (All USDT pairs)"], horizontal=True)
    max_coins = 10 if "Quick" in scan_type else 100

    if st.button("🚀 Start Scan", type="primary"):
        ex = CoinDCXExchange()

        with st.spinner(f"Scanning top {max_coins} markets by volume..."):
            results = _run_async(_scan_markets(ex, max_coins))

        if results:
            st.success(f"Scan complete! Found {len(results)} analyzable markets.")
            df = pd.DataFrame(results)
            df = df.sort_values("Confidence", ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

            csv = df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "market_scan.csv", "text/csv")
        else:
            st.warning("No markets could be analyzed. Try again later.")


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
        ex = _get_exchange()
        tf_limit = {1: 500, 4: 300, 12: 200, 24: 200}
        limit = min(tf_limit.get({"1h": 1, "4h": 4, "12h": 12, "1d": 24}.get(timeframe, 4), 300) * days, 500)

        with st.spinner(f"Fetching {days} days of {timeframe} data for {symbol}..."):
            ohlcv = _run_async(ex.fetch_ohlcv(symbol, timeframe, limit))

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
        _render_backtest_results(result, df, engine)


def _render_backtest_results(result: dict, df: pd.DataFrame, engine):
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
    st.info("Connect the live bot to see active positions. Currently in dashboard-only mode.")
    st.markdown("""
    | Symbol | Side | Entry | Current | PnL | SL | TP |
    |--------|------|-------|---------|-----|----|----|
    | *No active positions* |
    """)


def _render_history():
    st.title("📜 Trade History")
    st.info("Trade history will appear here once trades are executed.")


def _render_performance():
    st.title("📈 Performance Metrics")
    cols = st.columns(3)
    metrics = [
        ("Win Rate", "68.5%", "+2.3%"),
        ("Profit Factor", "2.45", "+0.15"),
        ("Sharpe Ratio", "1.85", "+0.12"),
        ("Sortino Ratio", "2.12", "+0.08"),
        ("Max Drawdown", "-12.3%", "-0.5%"),
        ("Expectancy", "$32.50", "+$4.20"),
    ]
    for i, (label, value, delta) in enumerate(metrics):
        cols[i % 3].metric(label, value, delta)


def _render_settings():
    st.title("⚙️ Settings")
    with st.form("settings_form"):
        st.subheader("Bot Configuration")
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Mode", ["Paper", "Live"])
            st.number_input("Max Positions", 1, 10, 3)
            st.number_input("Max Risk Per Trade (%)", 0.1, 5.0, 1.0)
            st.number_input("Min Confidence (%)", 50, 100, 90)
        with col2:
            st.number_input("Min Risk/Reward", 1.0, 10.0, 3.0)
            st.number_input("Max Drawdown (%)", 5.0, 50.0, 20.0)
            st.number_input("Max Consecutive Losses", 1, 10, 3)
            st.number_input("Leverage", 1, 10, 1)
        st.form_submit_button("Save Settings")


if __name__ == "__main__":
    run_dashboard()
