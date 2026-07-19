import asyncio
from typing import Any, Dict, List, Optional

import numpy as np
import streamlit as st

from src.config import settings, bot_config
from src.exchange.coindcx import CoinDCXExchange
from src.data.database import Database


_EXCHANGE: Optional[CoinDCXExchange] = None
_DB: Optional[Database] = None
_ASYNC_LOOP: asyncio.AbstractEventLoop = None


def _get_exchange():
    global _EXCHANGE
    if _EXCHANGE is None:
        _EXCHANGE = CoinDCXExchange()
    return _EXCHANGE


async def _fetch_all_tickers():
    ex = CoinDCXExchange()
    return await ex.fetch_all_tickers()


async def _fetch_ohlcv(symbol: str, timeframe: str, limit: int):
    ex = CoinDCXExchange()
    return await ex.fetch_ohlcv(symbol, timeframe, limit)


def _get_db():
    global _DB
    if _DB is None:
        _DB = Database()
        _run_async(_DB.initialize())
    return _DB


import nest_asyncio
nest_asyncio.apply()

def _run_async(coro):
    return asyncio.run(coro)


def _get_fetcher():
    if "fetcher" not in st.session_state:
        from src.data.fetcher import DataFetcher
        st.session_state.fetcher = DataFetcher(_get_exchange())
    return st.session_state.fetcher


def _fetch_trades(limit=100, status=None):
    try:
        db = _get_db()
        trades = _run_async(db.get_trades(limit=limit, status=status))
        return trades
    except Exception:
        return []


def _calc_metrics(trades):
    total = len(trades)
    if total == 0:
        return {}
    wins = [t for t in trades if t.pnl is not None and t.pnl > 0]
    losses = [t for t in trades if t.pnl is not None and t.pnl < 0]
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total * 100) if total > 0 else 0
    total_pnl = sum(t.pnl for t in trades if t.pnl is not None)
    avg_win = (sum(t.pnl for t in wins) / win_count) if win_count > 0 else 0
    avg_loss = (abs(sum(t.pnl for t in losses)) / loss_count) if loss_count > 0 else 0
    profit_factor = (sum(t.pnl for t in wins) / abs(sum(t.pnl for t in losses))) if loss_count > 0 and sum(t.pnl for t in losses) != 0 else (sum(t.pnl for t in wins) if win_count > 0 else 1)
    avg_trade = total_pnl / total if total > 0 else 0
    expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * avg_loss) if total > 0 else 0

    pnls = [t.pnl for t in trades if t.pnl is not None]
    if len(pnls) > 1:
        sharpe = (np.mean(pnls) / np.std(pnls) * np.sqrt(365)) if np.std(pnls) > 0 else 0
        neg_pnls = [p for p in pnls if p < 0]
        sortino = (np.mean(pnls) / np.std(neg_pnls) * np.sqrt(365)) if neg_pnls and np.std(neg_pnls) > 0 else 0
    else:
        sharpe = sortino = 0

    eq = []
    bal = 10000
    eq.append(bal)
    for t in trades:
        if t.pnl is not None:
            bal += t.pnl
            eq.append(bal)
    max_bal = eq[0]
    max_dd = 0
    for v in eq:
        max_bal = max(max_bal, v)
        dd = (max_bal - v) / max_bal * 100
        max_dd = max(max_dd, dd)

    return {
        "total_trades": total,
        "winning_trades": win_count,
        "losing_trades": loss_count,
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "profit_factor": round(profit_factor, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "max_drawdown": round(max_dd, 2),
        "average_trade": round(avg_trade, 2),
        "expectancy": round(expectancy, 2),
        "average_win": round(avg_win, 2),
        "average_loss": round(avg_loss, 2),
        "equity_curve": eq,
    }
