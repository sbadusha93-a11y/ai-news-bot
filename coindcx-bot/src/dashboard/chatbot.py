import asyncio
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import streamlit as st

from src.config import settings, bot_config
from src.dashboard.shared import _get_exchange, _get_db, _fetch_trades, _calc_metrics, _run_async, _get_fetcher, _fetch_all_tickers


_INTENTS = {
    r"(?i)\b(hi|hello|hey|greetings|sup|howdy)\b": "greeting",
    r"(?i)(price|rate|cost|worth|value)\s+(of\s+)?(\w+)": "price_check",
    r"(?i)(btc|bitcoin)\s*(price)?": "btc_price",
    r"(?i)(eth|ethereum)\s*(price)?": "eth_price",
    r"(?i)(top|best|biggest|highest).*(volume|gain|performer)": "top_markets",
    r"(?i)(pnl|profit|loss|performance|how.*doing)": "performance",
    r"(?i)(trade|position|open|active).*(count|number|how many|list)": "positions",
    r"(?i)(win.?rate|success.?rate|ratio)": "win_rate",
    r"(?i)(signal|scan|opportunity|setup).*(long|short|buy|sell)": "signals",
    r"(?i)(config|setting|mode|paper|live)": "settings",
    r"(?i)(help|what can you|commands|capabilities|features)": "help",
    r"(?i)(market|scanner|scan).*(active|signal)": "market_scan",
    r"(?i)(history|historic|past).*(trade|deal|order)": "trade_history",
    r"(?i)(conf|min_conf|confidence)": "confidence_info",
    r"(?i)(leverage|lever)": "leverage_info",
    r"(?i)(risk|drawdown|max_dd|stop.?loss|sl)": "risk_info",
    r"(?i)(status|health|bot.*running|uptime)": "bot_status",
    r"(?i)(balance|capital|equity|account)": "balance_info",
}


_INTENT_RESPONSES = {
    "greeting": lambda: f"Hello! I'm the CoinDCX Bot Assistant. I can help you with market prices, trades, performance, signals, and more. Type **help** to see what I can do.",
    "btc_price": lambda: _price_response("BTCUSDT", "Bitcoin"),
    "eth_price": lambda: _price_response("ETHUSDT", "Ethereum"),
    "help": lambda: (
        "Here's what I can help you with:\n\n"
        "💲 **Price** — `btc price`, `eth price`, `price of SOL`\n"
        "📊 **Markets** — `top markets`, `market scan`, `active signals`\n"
        "📈 **Performance** — `pnl`, `win rate`, `performance`\n"
        "📋 **Trades** — `positions`, `trade history`, `open trades`\n"
        "⚙️ **Settings** — `config`, `mode`, `leverage`, `risk`\n"
        "🔍 **Bot** — `status`, `balance`, `help`"
    ),
}


def _price_response(symbol_match: str, name: str):
    try:
        tickers = _run_async(_fetch_all_tickers())
        key = next((k for k in tickers if symbol_match in k), None)
        if not key:
            return f"Sorry, I couldn't find price data for {name}."
        t = tickers[key]
        price = t.get("last", 0)
        chg = t.get("percentage", 0)
        vol = t.get("volume", 0)
        high = t.get("high", 0)
        low = t.get("low", 0)
        return (
            f"**{name} ({key})**\n\n"
            f"💰 Price: `${price:,.4f}`\n"
            f"📈 24h Change: `{chg:+.2f}%`\n"
            f"📊 24h Volume: `{vol:,.2f}`\n"
            f"🔺 24h High: `${high:,.4f}`\n"
            f"🔻 24h Low: `${low:,.4f}`"
        )
    except Exception as e:
        return f"Error fetching {name} price: {e}"


def _get_ticker_for(symbol: str) -> Optional[Dict]:
    try:
        tickers = _run_async(_fetch_all_tickers())
        key = symbol.upper()
        if key in tickers:
            return tickers[key]
        for k in tickers:
            if key in k or key.replace("USDT", "") in k:
                return tickers[k]
        return None
    except Exception:
        return None


def _handle_price_check(match):
    coin = match.group(3).upper()
    if not coin.endswith("USDT"):
        coin = coin + "USDT" if not coin.endswith("USDT") else coin
    ticker = _get_ticker_for(coin)
    if ticker:
        price = ticker.get("last", 0)
        chg = ticker.get("percentage", 0)
        return f"**{coin}** Price: `${price:,.4f}` ({chg:+.2f}%)"
    return f"Sorry, I couldn't find price data for `{coin}`."


def _handle_top_markets():
    try:
        tickers = _run_async(_fetch_all_tickers())
        sorted_by_vol = sorted(
            [(s, t) for s, t in tickers.items() if t.get("volume", 0) > 0],
            key=lambda x: x[1]["volume"], reverse=True
        )[:10]
        lines = ["**Top 10 Markets by Volume**\n"]
        for i, (sym, t) in enumerate(sorted_by_vol, 1):
            lines.append(f"{i}. **{sym}** — `${t.get('last', 0):,.4f}` | Vol: `{t.get('volume', 0):,.0f}` | {t.get('percentage', 0):+.2f}%")
        return "\n".join(lines)
    except Exception as e:
        return f"Error fetching top markets: {e}"


def _handle_performance():
    trades = _fetch_trades(limit=500)
    m = _calc_metrics(trades)
    if not m:
        return "No trade data available yet."
    return (
        f"**Performance Overview**\n\n"
        f"📊 Total Trades: `{m['total_trades']}`\n"
        f"✅ Wins: `{m['winning_trades']}` | ❌ Losses: `{m['losing_trades']}`\n"
        f"🎯 Win Rate: `{m['win_rate']:.1f}%`\n"
        f"💰 Total P&L: `${m['total_pnl']:+,.2f}`\n"
        f"📈 Profit Factor: `{m['profit_factor']:.2f}`\n"
        f"📉 Max Drawdown: `{m['max_drawdown']:.2f}%`\n"
        f"⚡ Sharpe Ratio: `{m['sharpe_ratio']:.2f}`\n"
        f"📊 Avg Trade: `${m['average_trade']:+,.2f}`"
    )


def _handle_positions():
    open_trades = _fetch_trades(status="open")
    if not open_trades:
        return "No active positions currently."
    lines = [f"**Active Positions ({len(open_trades)})**\n"]
    for t in open_trades:
        sym = t.symbol.replace("_", "/")
        side = t.side.upper()
        entry = t.entry_price or 0
        qty = t.quantity or 0
        lines.append(f"• {sym} | {side} | Entry: `${entry:.4f}` | Qty: `{qty}`")
    return "\n".join(lines)


def _handle_win_rate():
    trades = _fetch_trades(limit=500)
    m = _calc_metrics(trades)
    if not m:
        return "No trade data yet."
    return (
        f"**Win Rate Analysis**\n\n"
        f"Win Rate: `{m['win_rate']:.1f}%` ({m['winning_trades']}W / {m['losing_trades']}L)\n"
        f"Avg Win: `${m['average_win']:+,.2f}`\n"
        f"Avg Loss: `${m['average_loss']:+,.2f}`\n"
        f"Expectancy: `${m['expectancy']:+,.2f}` per trade"
    )


def _handle_signals():
    if "scanner_signals" not in st.session_state or not st.session_state.scanner_signals:
        return "No active signals. Run a market scan from the **Market Scanner** page first."
    signals = st.session_state.scanner_signals
    longs = [s for s in signals if s["signal"] == "LONG"]
    shorts = [s for s in signals if s["signal"] == "SHORT"]
    lines = [f"**Active Signals ({len(signals)} total)**\n"]
    if longs:
        lines.append(f"🟢 **LONG** ({len(longs)}):")
        for s in longs[:5]:
            lines.append(f"  • {s['symbol']} @ `${s['entry_price']:.4f}` (Conf: `{s['confidence']:.0f}%`)")
    if shorts:
        lines.append(f"🔴 **SHORT** ({len(shorts)}):")
        for s in shorts[:5]:
            lines.append(f"  • {s['symbol']} @ `${s['entry_price']:.4f}` (Conf: `{s['confidence']:.0f}%`)")
    return "\n".join(lines)


def _handle_settings():
    return (
        f"**Bot Configuration**\n\n"
        f"🔄 Mode: `{settings.bot_mode.upper()}`\n"
        f"📦 Max Positions: `{bot_config['bot']['max_positions']}`\n"
        f"🎯 Min Confidence: `{bot_config['bot']['min_confidence']}%`\n"
        f"📊 Min R:R: `1:{bot_config['bot']['min_rr']}`\n"
        f"⚡ Leverage: `{bot_config['bot']['leverage']}x`\n"
        f"🛡️ Max Risk/Trade: `{bot_config['risk']['max_risk_per_trade']}%`\n"
        f"📉 Max Drawdown: `{bot_config['risk']['max_drawdown']}%`"
    )


def _handle_market_scan():
    if "scanner_signals" not in st.session_state or not st.session_state.scanner_signals:
        return "No market scan data in session. Go to **Market Scanner** and run a scan first."
    signals = st.session_state.scanner_signals
    long_c = sum(1 for s in signals if s["signal"] == "LONG")
    short_c = sum(1 for s in signals if s["signal"] == "SHORT")
    neutral_c = sum(1 for s in signals if s["signal"] == "NEUTRAL")
    return f"**Market Scan Summary**\n\n🟢 LONG: `{long_c}` | 🔴 SHORT: `{short_c}` | ⚪ Neutral: `{neutral_c}`\nTotal markets scanned: `{len(signals)}`"


def _handle_trade_history():
    trades = _fetch_trades(limit=20)
    if not trades:
        return "No trade history yet."
    lines = ["**Recent Trades (last 20)**\n"]
    for t in reversed(trades[-10:]):
        sym = t.symbol.replace("_", "/")
        side = t.side.upper()
        pnl = f"${t.pnl:+,.2f}" if t.pnl is not None else "—"
        status = t.status.upper()
        lines.append(f"• {sym} | {side} | PnL: `{pnl}` | Status: `{status}`")
    return "\n".join(lines)


def _handle_confidence_info():
    return f"The bot requires a minimum confidence score of **{bot_config['bot']['min_confidence']}%** before entering a trade. Confidence is calculated based on technical indicators (RSI, MACD, ADX, SMC patterns, etc.) and weighted scoring."


def _handle_leverage_info():
    return f"Current leverage setting: **{bot_config['bot']['leverage']}x**. You can change this in **Settings**. Higher leverage increases both potential profits and risks."


def _handle_risk_info():
    return (
        f"**Risk Parameters**\n\n"
        f"🛡️ Max Risk Per Trade: `{bot_config['risk']['max_risk_per_trade']}%`\n"
        f"📉 Max Drawdown: `{bot_config['risk']['max_drawdown']}%`\n"
        f"🔄 Consecutive Losses Limit: `{bot_config['risk']['max_consecutive_losses']}`\n"
        f"⏸️ Max Daily Risk: `{bot_config['risk']['max_daily_risk']}%`\n"
        f"📊 ATR Stop Loss Multiplier: `{bot_config['risk']['stop_loss_atr_multiplier']}x`"
    )


def _handle_bot_status():
    try:
        trades = _fetch_trades(limit=1)
        tickers = _run_async(_fetch_all_tickers())
        return (
            f"**Bot Status**\n\n"
            f"✅ Bot is running\n"
            f"🔄 Mode: `{settings.bot_mode.upper()}`\n"
            f"📊 Markets tracked: `{len(tickers)}`\n"
            f"📋 Open positions: `{len(_fetch_trades(status='open'))}`\n"
            f"⚡ Exchange: `CoinDCX`"
        )
    except Exception as e:
        return f"⚠️ Bot status check failed: {e}"


def _handle_balance_info():
    trades = _fetch_trades(limit=500)
    m = _calc_metrics(trades)
    if not m:
        return "No trade data to estimate balance."
    eq = m.get("equity_curve", [10000])
    current_bal = eq[-1]
    initial = eq[0]
    return (
        f"**Account Overview**\n\n"
        f"💰 Estimated Balance: `${current_bal:+,.2f}`\n"
        f"📈 Total Return: `{((current_bal - initial) / initial * 100):+.2f}%`\n"
        f"📊 Total P&L: `${m['total_pnl']:+,.2f}`\n"
        f"📉 Max Drawdown: `{m['max_drawdown']:.2f}%`"
    )


_HANDLERS = {
    "price_check": _handle_price_check,
    "top_markets": _handle_top_markets,
    "performance": _handle_performance,
    "positions": _handle_positions,
    "win_rate": _handle_win_rate,
    "signals": _handle_signals,
    "settings": _handle_settings,
    "market_scan": _handle_market_scan,
    "trade_history": _handle_trade_history,
    "confidence_info": _handle_confidence_info,
    "leverage_info": _handle_leverage_info,
    "risk_info": _handle_risk_info,
    "bot_status": _handle_bot_status,
    "balance_info": _handle_balance_info,
}


def classify_intent(text: str) -> Optional[str]:
    for pattern, intent in _INTENTS.items():
        m = re.search(pattern, text)
        if m:
            return intent
    return None


def generate_response(user_input: str) -> str:
    intent = classify_intent(user_input)
    if intent in _INTENT_RESPONSES:
        return _INTENT_RESPONSES[intent]()
    if intent in _HANDLERS:
        match = re.search(list(k for k, v in _INTENTS.items() if v == intent)[0], user_input) if intent == "price_check" else None
        return _HANDLERS[intent](match) if match and intent == "price_check" else _HANDLERS[intent]()
    return (
        f"I'm not sure how to answer that. I can help with prices, trades, performance, signals, settings, and bot status. "
        f"Type **help** to see what I can do.\n\n"
        f"*You said: \"{user_input}\"*"
    )


def render_chatbot():
    st.title("🤖 AI Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I'm your CoinDCX trading assistant. Ask me about prices, performance, trades, signals, or bot settings."}
        ]

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask me anything about your bot...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = generate_response(prompt)
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

    if st.session_state.chat_history:
        st.button("🗑️ Clear Chat", on_click=lambda: st.session_state.update(chat_history=[]), type="secondary")
