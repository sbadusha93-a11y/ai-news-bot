#!/usr/bin/env python3
import asyncio
import sys
sys.path.insert(0, ".")

from src.config import bot_config
from src.exchange.coindcx import CoinDCXExchange
from src.backtest.engine import BacktestEngine
import pandas as pd


async def run_bt():
    ex = CoinDCXExchange()
    engine = BacktestEngine(initial_balance=10000.0)
    symbols = ["BTC_USDT", "ETH_USDT", "SOL_USDT", "BNB_USDT", "XRP_USDT"]
    results = {}
    for sym in symbols:
        print(f"Fetching {sym} 4h data...")
        ohlcv = await ex.fetch_ohlcv(sym, "4h", 2000)
        if not ohlcv or len(ohlcv) < 100:
            print(f"  Not enough data: {len(ohlcv) if ohlcv else 0}")
            continue
        df = pd.DataFrame(ohlcv, columns=["timestamp","open","high","low","close","volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)
        print(f"  {len(df)} candles: {df.index[0].date()} to {df.index[-1].date()}")
        result = await engine.run(df, symbol=sym, slippage=0.001, commission=0.00075)
        results[sym] = result
        print(f"  Result: {result.get('total_trades',0)} trades")
        print(f"  PnL: ${result.get('net_profit',0):.2f} ({result.get('total_return',0):.1f}%)")
        print(f"  Sharpe: {result.get('sharpe_ratio',0):.2f} | Win: {result.get('win_rate',0):.1f}%")
    await ex.close()
    return results


r = asyncio.run(run_bt())
print()
print("=" * 70)
print("BACKTEST SUMMARY")
print("=" * 70)
for sym, res in r.items():
    print(f"\n{sym}:")
    print(f"  Trades: {res.get('total_trades',0)}")
    print(f"  Win Rate: {res.get('win_rate',0):.1f}%")
    print(f"  Profit Factor: {res.get('profit_factor',0):.2f}")
    print(f"  Net Profit: ${res.get('net_profit',0):.2f}")
    print(f"  Total Return: {res.get('total_return',0):.1f}%")
    print(f"  Max DD: {res.get('max_drawdown',0):.1f}%")
    print(f"  Sharpe: {res.get('sharpe_ratio',0):.2f}")
    print(f"  Sortino: {res.get('sortino_ratio',0):.2f}")
    print(f"  Avg Trade: ${res.get('average_trade',0):.2f}")
    print(f"  Avg Win: ${res.get('average_win',0):.2f}")
    print(f"  Avg Loss: ${res.get('average_loss',0):.2f}")
    print(f"  Expectancy: ${res.get('expectancy',0):.4f}")
    print(f"  Recovery Factor: {res.get('recovery_factor',0):.2f}")
    print(f"  Final Balance: ${res.get('final_balance',0):.2f}")
