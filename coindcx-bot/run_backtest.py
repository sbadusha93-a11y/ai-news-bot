import asyncio
import sys
from datetime import datetime, timedelta

from loguru import logger

from src.backtest.engine import BacktestEngine
from src.config import bot_config
from src.data.fetcher import DataFetcher
from src.exchange.coindcx import CoinDCXExchange


logger.remove()
logger.add(lambda _: None, level="ERROR")


async def main():
    exchange = CoinDCXExchange()
    fetcher = DataFetcher(exchange)

    tf = bot_config["timeframes"]["primary"]
    lookback_days = 60

    print("=" * 80)
    print(f"BACKTEST: {tf} timeframe | Config: 1h-adjusted")
    print(f"  Confirmations: {bot_config['timeframes']['confirmation']}")
    print(f"  Min RR: {bot_config['bot']['min_rr']} | Min Conf: {bot_config['bot']['min_confidence']}")
    print(f"  SL: {bot_config['risk']['stop_loss_atr_multiplier']}x ATR")
    print(f"  TP: {[l['ratio'] for l in bot_config['risk']['take_profit_levels']]}x risk")
    print(f"  Daily risk: {bot_config['risk']['max_daily_risk']}% | Per trade: {bot_config['risk']['max_risk_per_trade']}%")
    print(f"  Data: {lookback_days} days of {tf} candles")
    print("=" * 80)

    print("\nFetching top markets...")
    markets = await fetcher.scan_all_markets()
    if markets.empty:
        print("No markets found. Check API connectivity.")
        await exchange.close()
        return

    print(f"Found {len(markets)} tradeable pairs\n")

    all_results = {}
    total_trades = 0
    total_profit = 0.0
    total_wins = 0
    total_losses = 0

    symbols = markets["symbol"].tolist()[:10]
    from_date = datetime.now() - timedelta(days=lookback_days)

    for symbol in symbols:
        print(f"{'='*80}")
        print(f"TESTING: {symbol}")
        print(f"{'='*80}")

        df = await fetcher.fetch_historical_data(symbol, tf, limit=5000, from_date=from_date)
        if df.empty or len(df) < 100:
            print(f"  SKIP: insufficient data")
            continue

        n_candles = len(df)
        start = df.index[0].strftime("%Y-%m-%d")
        end = df.index[-1].strftime("%Y-%m-%d")
        days = (df.index[-1] - df.index[0]).days
        print(f"  Candles: {n_candles} ({start} to {end} = ~{days}d)")
        print(f"  Price: ${df['low'].min():.4f} - ${df['high'].max():.4f}")

        engine = BacktestEngine(initial_balance=10000.0)
        result = await engine.run(df, symbol=symbol)

        if "error" in result:
            print(f"  ERROR: {result['error']}")
            continue

        total_trades += result["total_trades"]
        total_profit += result["net_profit"]
        total_wins += result["winning_trades"]
        total_losses += result["losing_trades"]

        all_results[symbol] = result

        pnl_str = f"${result['net_profit']:+.2f}" if result["total_trades"] > 0 else "N/A"
        print(f"  Trades: {result['total_trades']} | Win: {result['win_rate']}% | PnL: {pnl_str}")
        if result["total_trades"] > 0:
            print(f"  Return: {result['total_return']:+.2f}% | MaxDD: {result['max_drawdown']}%")
            print(f"  PF: {result['profit_factor']} | Sharpe: {result['sharpe_ratio']} | Expectancy: ${result['expectancy']:.4f}")

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    tested = len(all_results)
    print(f"Symbols: {tested}/{len(symbols)}")
    print(f"Total trades: {total_trades}")

    if total_trades > 0:
        overall_win_rate = total_wins / total_trades * 100
        print(f"Total PnL: ${total_profit:+.2f}")
        print(f"Win rate: {overall_win_rate:.1f}% ({total_wins}W / {total_losses}L)")
        print(f"Avg profit/symbol: ${total_profit / tested:.2f}" if tested > 0 else "")

        print()
        print(f"{'Symbol':<12} {'Trades':<7} {'Win%':<7} {'PnL':<11} {'Return':<9} {'MaxDD':<8} {'PF':<7} {'Sharpe':<8}")
        print("-" * 69)
        sorted_syms = sorted(all_results.items(), key=lambda x: x[1]["net_profit"], reverse=True)
        for sym, r in sorted_syms:
            if r["total_trades"] > 0:
                print(f"{sym:<12} {r['total_trades']:<7} {r['win_rate']:<6.1f}% "
                      f"${r['net_profit']:<+8.2f} {r['total_return']:<+7.2f}% "
                      f"{r['max_drawdown']:<6.2f}% {r['profit_factor']:<6.2f} {r['sharpe_ratio']:<7.4f}")
            else:
                print(f"{sym:<12} {0:<7} {'N/A':<7} {'N/A':<11}")

        profitable = sum(1 for r in all_results.values() if r["net_profit"] > 0)
        print("-" * 69)
        print(f"Profitable symbols: {profitable}/{tested}")

        if total_profit > 0:
            print(f"\nResult: PROFITABLE (${total_profit:+.2f}) over {lookback_days}-day period")
        else:
            print(f"\nResult: NOT PROFITABLE (${total_profit:+.2f}) over {lookback_days}-day period")
    else:
        print("No trades generated at all.")

    await exchange.close()


if __name__ == "__main__":
    asyncio.run(main())
