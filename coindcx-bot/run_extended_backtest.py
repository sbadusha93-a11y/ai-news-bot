#!/usr/bin/env python3
"""Extended backtest: 20+ symbols, multiple timeframes, detailed report."""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, ".")

import pandas as pd
from loguru import logger

from src.config import bot_config
from src.exchange.coindcx import CoinDCXExchange
from src.backtest.engine import BacktestEngine

# Top 20 USDT pairs by volume
SYMBOLS = [
    "BTC_USDT", "ETH_USDT", "BNB_USDT", "SOL_USDT", "XRP_USDT",
    "ADA_USDT", "DOGE_USDT", "DOT_USDT", "LINK_USDT", "AVAX_USDT",
    "MATIC_USDT", "ATOM_USDT", "UNI_USDT", "LTC_USDT", "BCH_USDT",
    "XLM_USDT", "TRX_USDT", "FIL_USDT", "APT_USDT", "ARB_USDT",
]

TIMEFRAMES = ["1h", "4h"]
CANDLE_LIMITS = {"1h": 1000, "4h": 500}
RESULTS_FILE = "backtest_results.json"


def _safe_val(d, key, default=0):
    v = d.get(key, default)
    if v is None or (isinstance(v, float) and (v != v or v == float("inf") or v == -float("inf"))):
        return default
    return v


async def run_backtest_for_symbol(ex, symbol, timeframe, limit):
    ohlcv = await ex.fetch_ohlcv(symbol, timeframe, limit)
    if not ohlcv or len(ohlcv) < 100:
        return None
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)
    engine = BacktestEngine(initial_balance=10000.0)
    result = await engine.run(df, symbol=symbol, slippage=0.001, commission=0.00075)
    result["symbol"] = symbol
    result["timeframe"] = timeframe
    result["candles"] = len(df)
    result["date_from"] = str(df.index[0].date())
    result["date_to"] = str(df.index[-1].date())
    return result


async def main():
    print("=" * 80)
    print(f"  EXTENDED BACKTEST — {len(SYMBOLS)} symbols × {len(TIMEFRAMES)} timeframes")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    ex = CoinDCXExchange()
    all_results = {}
    total_start = time.time()

    for timeframe in TIMEFRAMES:
        print(f"\n--- TIMEFRAME: {timeframe} ---")
        tf_results = {}
        for i, sym in enumerate(SYMBOLS):
            start = time.time()
            print(f"  [{i+1}/{len(SYMBOLS)}] {sym} {timeframe}... ", end="", flush=True)
            try:
                result = await run_backtest_for_symbol(ex, sym, timeframe, CANDLE_LIMITS[timeframe])
                elapsed = time.time() - start
                if result and result.get("total_trades", 0) > 0:
                    print(f"{result['total_trades']} trades, "
                          f"PnL: ${_safe_val(result,'net_profit'):.2f}, "
                          f"Win: {_safe_val(result,'win_rate'):.1f}%, "
                          f"Sharpe: {_safe_val(result,'sharpe_ratio'):.2f} "
                          f"[{elapsed:.1f}s]")
                    tf_results[sym] = result
                elif result:
                    print(f"0 trades [{elapsed:.1f}s]")
                else:
                    print(f"NO DATA [{elapsed:.1f}s]")
            except Exception as e:
                print(f"ERROR: {e}")
            await asyncio.sleep(0.5)
        all_results[timeframe] = tf_results

    await ex.close()

    total_elapsed = time.time() - total_start
    print(f"\n{'=' * 80}")
    print(f"  BACKTEST COMPLETE — {total_elapsed:.1f}s total")
    print(f"{'=' * 80}")

    # Compute aggregate stats per timeframe
    for tf, results in all_results.items():
        if not results:
            print(f"\n--- {tf}: No trading opportunities found ---")
            continue
        traded = [r for r in results.values() if r.get("total_trades", 0) > 0]
        nontraded = [s for s, r in results.items() if r.get("total_trades", 0) == 0]
        total_trades = sum(r.get("total_trades", 0) for r in results.values())
        winning = sum(1 for r in results.values() if r.get("net_profit", 0) > 0)
        total_pnl = sum(_safe_val(r, "net_profit") for r in results.values())
        avg_win_rate = sum(_safe_val(r, "win_rate") for r in traded) / len(traded) if traded else 0
        avg_sharpe = sum(_safe_val(r, "sharpe_ratio") for r in traded) / len(traded) if traded else 0
        avg_profit_factor = sum(_safe_val(r, "profit_factor") for r in traded) / len(traded) if traded else 0
        max_dd = max(_safe_val(r, "max_drawdown") for r in results.values()) if results else 0
        avg_return = sum(_safe_val(r, "total_return") for r in results.values())

        print(f"\n{'=' * 60}")
        print(f"  TIMEFRAME: {tf}")
        print(f"{'=' * 60}")
        print(f"  Traded symbols:   {len(traded)}/{len(results)}")
        print(f"  Total trades:     {total_trades}")
        print(f"  Profitable syms:  {winning}/{len(results)}")
        print(f"  Total PnL:        ${total_pnl:.2f}")
        print(f"  Avg Return:       {avg_return:.2f}%")
        print(f"  Avg Win Rate:     {avg_win_rate:.1f}%")
        print(f"  Avg Profit Fac:   {avg_profit_factor:.2f}")
        print(f"  Avg Sharpe:       {avg_sharpe:.2f}")
        print(f"  Worst DD:         {max_dd:.1f}%")
        if nontraded:
            print(f"  No trades:        {', '.join(nontraded[:10])}{'...' if len(nontraded)>10 else ''}")

        # Best performers
        sorted_by_pnl = sorted(results.items(), key=lambda x: _safe_val(x[1], "net_profit"), reverse=True)
        print(f"\n  TOP 5 (by PnL):")
        for sym, r in sorted_by_pnl[:5]:
            if r.get("total_trades", 0) > 0:
                print(f"    {sym:12s}  {r['total_trades']:2d} trades  "
                      f"${_safe_val(r,'net_profit'):>8.2f}  "
                      f"{_safe_val(r,'win_rate'):5.1f}% WR  "
                      f"PF {_safe_val(r,'profit_factor'):.2f}  "
                      f"S {_safe_val(r,'sharpe_ratio'):.2f}  "
                      f"DD {_safe_val(r,'max_drawdown'):.1f}%")
        sorted_by_sharpe = sorted(results.items(), key=lambda x: _safe_val(x[1], "sharpe_ratio"), reverse=True)
        print(f"\n  TOP 5 (by Sharpe):")
        for sym, r in sorted_by_sharpe[:5]:
            if r.get("total_trades", 0) > 0 and _safe_val(r, "sharpe_ratio") > 0:
                print(f"    {sym:12s}  S {_safe_val(r,'sharpe_ratio'):.2f}  "
                      f"${_safe_val(r,'net_profit'):>8.2f}  "
                      f"{_safe_val(r,'win_rate'):5.1f}% WR  "
                      f"PF {_safe_val(r,'profit_factor'):.2f}  "
                      f"{r['total_trades']:2d} trades")

    # Save full results
    serializable = {}
    for tf, results in all_results.items():
        serializable[tf] = {
            sym: {k: v for k, v in r.items() if not isinstance(v, (pd.Timestamp, pd.Series))}
            for sym, r in results.items()
        }
    with open(RESULTS_FILE, "w") as f:
        json.dump(serializable, f, indent=2, default=str)
    print(f"\nFull results saved to {RESULTS_FILE}")

    # Compute overall recommendation
    print(f"\n{'=' * 80}")
    print(f"  OVERALL ASSESSMENT")
    print(f"{'=' * 80}")
    all_traded = [r for tf_res in all_results.values() for r in tf_res.values() if r.get("total_trades", 0) > 0]
    if not all_traded:
        print("  No trading opportunities found across any timeframe.")
        print("  Recommendation: Review strategy parameters and scoring thresholds.")
        return
    total_all = sum(r.get("total_trades", 0) for r in all_traded)
    avg_wr = sum(_safe_val(r, "win_rate") for r in all_traded) / len(all_traded)
    avg_sr = sum(_safe_val(r, "sharpe_ratio") for r in all_traded) / len(all_traded)
    avg_pf = sum(_safe_val(r, "profit_factor") for r in all_traded) / len(all_traded)
    total_pnl_all = sum(_safe_val(r, "net_profit") for r in all_traded)
    worst_dd = max(_safe_val(r, "max_drawdown") for r in all_traded)

    print(f"  Total symbols traded:    {len(all_traded)}")
    print(f"  Total trades executed:   {total_all}")
    print(f"  Combined PnL:            ${total_pnl_all:.2f}")
    print(f"  Avg Win Rate:            {avg_wr:.1f}%")
    print(f"  Avg Profit Factor:       {avg_pf:.2f}")
    print(f"  Avg Sharpe Ratio:        {avg_sr:.2f}")
    print(f"  Worst Drawdown:          {worst_dd:.1f}%")

    if avg_wr >= 50 and avg_pf >= 1.5 and avg_sr >= 1.0:
        print(f"\n  ✅ VERDICT: Strategy is profitable. Ready for paper trading.")
    elif avg_wr >= 40 and avg_pf >= 1.0:
        print(f"\n  ⚠️  VERDICT: Marginally profitable. Consider parameter tuning.")
    else:
        print(f"\n  ❌ VERDICT: Strategy needs improvement before paper trading.")


if __name__ == "__main__":
    asyncio.run(main())
