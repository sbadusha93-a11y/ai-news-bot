from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger

from src.config import bot_config
from src.indicators.technical import TechnicalIndicators
from src.indicators.smc import SMCIndicators
from src.indicators.volume import VolumeIndicators
from src.indicators.price_action import PriceActionIndicators
from src.ml.predictor import MLPredictor
from src.risk.manager import RiskManager
from src.risk.sizing import PositionSizer
from src.strategy.engine import StrategyEngine
from src.strategy.scorer import TradeScorer


class BacktestEngine:
    def __init__(self, initial_balance: float = 10000.0):
        self.initial_balance = initial_balance
        self.risk_manager = RiskManager()
        self.position_sizer = PositionSizer(initial_balance)
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = [initial_balance]
        self._current_day = None
        self._current_week = None
        self._max_positions = 3
        self._active_count = 0

    async def run(
        self,
        df: pd.DataFrame,
        symbol: str = "BACKTEST",
        slippage: float = 0.001,
        commission: float = 0.00075,
    ) -> Dict[str, Any]:
        if df.empty or len(df) < 100:
            return {"error": "Insufficient data"}
        df = df.copy()
        technical = TechnicalIndicators()
        smc = SMCIndicators()
        volume = VolumeIndicators()
        pa = PriceActionIndicators()
        scorer = TradeScorer()

        df = technical.compute_all(df)
        df = smc.compute_all(df)
        df = volume.compute_all(df)
        df = pa.compute_all(df)

        daily = df.resample("D").agg({
            "open": "first", "high": "max", "low": "min",
            "close": "last", "volume": "sum"
        }).dropna()
        daily_tech = TechnicalIndicators()
        daily = daily_tech.compute_all(daily)

        position = None
        balance = float(self.initial_balance)
        self.trades = []
        self.equity_curve = [balance]

        for i in range(60, len(df)):
            row = df.iloc[:i + 1]
            current = df.iloc[i]
            price = float(current["close"])

            self._handle_time_resets(df, i)

            if position:
                sl = position["stop_loss"]
                tp1 = position.get("take_profit_1", 0)
                tp2 = position.get("take_profit_2", 0)
                direction = position["side"]
                entry = position["entry_price"]
                high, low = float(current["high"]), float(current["low"])
                qty = position["quantity"]

                exit_reason = None
                exit_price = None

                if position.get("trailing_active"):
                    extreme = high if direction == "long" else low
                    trail_dist = abs(entry - position["stop_loss"]) * 0.25
                    new_sl = extreme - trail_dist if direction == "long" else extreme + trail_dist
                    if direction == "long":
                        sl = max(sl, new_sl)
                        position["stop_loss"] = sl
                    else:
                        sl = min(sl, new_sl)
                        position["stop_loss"] = sl
                    position["trailing_high"] = max(position.get("trailing_high", entry), extreme)

                if direction == "long":
                    if tp1 > 0 and high >= tp1 and not position.get("tp1_hit"):
                        exit_reason = "take_profit_partial"
                        exit_price = tp1
                    elif tp2 > 0 and high >= tp2:
                        exit_reason = "take_profit"
                        exit_price = tp2
                    elif low <= sl:
                        exit_reason = "stop_loss"
                        exit_price = sl
                else:
                    if tp1 > 0 and low <= tp1 and not position.get("tp1_hit"):
                        exit_reason = "take_profit_partial"
                        exit_price = tp1
                    elif tp2 > 0 and low <= tp2:
                        exit_reason = "take_profit"
                        exit_price = tp2
                    elif high >= sl:
                        exit_reason = "stop_loss"
                        exit_price = sl

                if exit_reason == "take_profit_partial":
                    half_qty = qty * 0.5
                    pnl, _ = self._compute_pnl(entry, exit_price, half_qty, direction, commission)
                    balance += pnl
                    position["quantity"] = qty - half_qty
                    be_buffer = entry * 0.008
                    position["stop_loss"] = entry + be_buffer if direction == "long" else entry - be_buffer
                    position["tp1_hit"] = True
                    position["take_profit_1"] = 0
                    position["trailing_active"] = True
                    position["trailing_high"] = entry
                    self.equity_curve.append(balance)
                    half_rec = position.copy()
                    half_rec["quantity"] = half_qty
                    half_rec["pnl"] = round(pnl, 2)
                    half_rec["reason_exit"] = "partial_tp1"
                    half_rec["exit_price"] = round(exit_price, 8)
                    half_rec["exit_time"] = df.index[i]
                    self.trades.append(half_rec)
                    continue

                if exit_reason:
                    exit_with_slip = exit_price * (1 - slippage) if direction == "long" else exit_price * (1 + slippage)
                    pnl, pnl_pct = self._compute_pnl(entry, exit_with_slip, qty, direction, commission)
                    balance += pnl
                    position.update({
                        "exit_price": round(exit_with_slip, 8),
                        "pnl": round(pnl, 2),
                        "pnl_percent": round(pnl_pct, 2),
                        "reason_exit": exit_reason,
                        "exit_time": df.index[i],
                    })
                    self.trades.append(position)
                    self.equity_curve.append(balance)
                    self.risk_manager.record_trade(position)
                    position = None
                    self._active_count -= 1
                    self.position_sizer.update_balance(balance)
                    continue

            if not position and self._active_count < self._max_positions and self.risk_manager.can_trade():
                df_dict = {bot_config["timeframes"]["primary"]: row}
                analysis = await self._simulate_analysis(df_dict, scorer, smc, volume, pa)
                signals = analysis.get("signals", {})
                conf = signals.get("confidence", 0)

                if conf >= 75:
                    direction = signals.get("direction", "neutral")
                    if direction not in ("long", "short"):
                        continue

                    daily_date = df.index[i].normalize()
                    daily_row = daily.loc[daily_date] if daily_date in daily.index else None
                    if daily_row is not None:
                        d_close = float(daily_row["close"])
                        d_ema20 = float(daily_row.get("ema_20", d_close))
                        if direction == "long" and not (d_close > d_ema20):
                            continue
                        if direction == "short" and not (d_close < d_ema20):
                            continue

                    candle_confirm = (direction == "long" and float(current["close"]) > float(current["open"])) or \
                                     (direction == "short" and float(current["close"]) < float(current["open"]))
                    if not candle_confirm:
                        continue

                    atr_val = float(current.get("atr", price * 0.02))
                    sl_price = self.position_sizer.calculate_stop_loss(price, atr_val, direction)
                    tps = self.position_sizer.calculate_take_profits(price, sl_price, direction)
                    pos_size = self.position_sizer.calculate_position_size(price, sl_price)

                    if "error" not in pos_size:
                        rr = abs(tps.get(1, price) - price) / abs(price - sl_price)
                        if rr >= 1.2:
                            cost = price * pos_size["position_size"]
                            if cost <= balance:
                                entry_with_slip = price * (1 + slippage) if direction == "long" else price * (1 - slippage)
                                position = {
                                    "symbol": symbol,
                                    "side": direction,
                                    "entry_price": round(entry_with_slip, 8),
                                    "quantity": pos_size["position_size"],
                                    "stop_loss": sl_price,
                                    "take_profit_1": tps.get(1, 0),
                                    "take_profit_2": tps.get(2, 0),
                                    "entry_time": df.index[i],
                                    "status": "open",
                                    "trailing_active": False,
                                }
                                self._active_count += 1

        if position:
            current = df.iloc[-1]
            exit_price = float(current["close"])
            exit_with_slip = exit_price * (1 - slippage) if position["side"] == "long" else exit_price * (1 + slippage)
            pnl, pnl_pct = self._compute_pnl(
                position["entry_price"], exit_with_slip, position["quantity"], position["side"], commission
            )
            balance += pnl
            position.update({
                "exit_price": round(exit_with_slip, 8),
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_pct, 2),
                "reason_exit": "end_of_backtest",
            })
            self.trades.append(position)
            self.equity_curve.append(balance)

        self.balance = balance
        return self._compute_metrics()

    async def _simulate_analysis(
        self, df_dict: Dict, scorer: TradeScorer,
        smc: SMCIndicators, volume: VolumeIndicators, pa: PriceActionIndicators,
    ) -> Dict:
        analysis = {"timeframes": {}, "overall": {}, "signals": {}, "sentiment": {}}
        for tf, df in df_dict.items():
            last = df.iloc[-1]
            regime = self._detect_regime_simple(df)
            trend = self._determine_trend(df)
            score = self._compute_bt_score(df)
            analysis["timeframes"][tf] = {
                "last_row": last.to_dict() if not last.empty else {},
                "technical_score": score * 2,
                "smc_score": 0.0,
                "volume_score": 0.0,
                "price_action_score": 0.0,
                "ml_score": 0.0,
                "ml_confidence": 0.0,
                "trend": trend,
                "regime": regime,
                "support": 0,
                "resistance": 0,
            }
        analysis["overall"] = self._compute_overall_simple(analysis["timeframes"])
        analysis["signals"] = scorer.compute_signals(analysis)
        return analysis

    def _compute_bt_score(self, df: pd.DataFrame) -> float:
        if df.empty:
            return 0.0
        last = df.iloc[-1]
        score = 0.0
        if last.get("rsi", 50) < 35:
            score += 6
        elif last.get("rsi", 50) > 65:
            score -= 6
        if last.get("macd_signal_line") == "bullish":
            score += 8
        elif last.get("macd_signal_line") == "bearish":
            score -= 8
        if last.get("ema_9_20_cross") == "bullish":
            score += 5
        elif last.get("ema_9_20_cross") == "bearish":
            score -= 5
        if last.get("st_direction") == "uptrend":
            score += 8
        elif last.get("st_direction") == "downtrend":
            score -= 8
        if last.get("obv_signal") == "bullish":
            score += 4
        elif last.get("obv_signal") == "bearish":
            score -= 4
        if abs(score) >= 10:
            return score
        return 0.0

    def _detect_regime_simple(self, df: pd.DataFrame) -> Dict:
        if df.empty or len(df) < 30:
            return {"trend": "sideways", "volatility": "normal", "is_tradeable": True}
        last = df.iloc[-1]
        adx = last.get("adx", 0)
        close = last["close"]
        ema_50 = last.get("ema_50", close)
        ema_200 = last.get("ema_200", close)
        if close > ema_50 > ema_200 and adx > 25:
            trend = "strong_uptrend"
        elif close < ema_50 < ema_200 and adx > 25:
            trend = "strong_downtrend"
        elif close > ema_50 > ema_200:
            trend = "weak_uptrend"
        elif close < ema_50 < ema_200:
            trend = "weak_downtrend"
        else:
            trend = "sideways"
        atr_pct = last.get("atr_percent", 0)
        vol = "high" if atr_pct > 5 else "normal" if atr_pct > 1 else "low"
        return {"trend": trend, "volatility": vol, "is_tradeable": trend != "sideways" and vol != "extreme"}

    def _determine_trend(self, df: pd.DataFrame) -> str:
        if df.empty:
            return "neutral"
        last = df.iloc[-1]
        close = last["close"]
        ema_50 = last.get("ema_50", close)
        ema_200 = last.get("ema_200", close)
        if close > ema_50 > ema_200:
            return "bullish"
        elif close < ema_50 < ema_200:
            return "bearish"
        return "sideways"

    def _compute_overall_simple(self, timeframes: Dict) -> Dict:
        total_score = 0.0
        trend_counts = {"bullish": 0, "bearish": 0, "sideways": 0}
        for tf, data in timeframes.items():
            total_score += data.get("technical_score", 0)
            trend_counts[data.get("trend", "sideways")] += 1
        max_trend = max(trend_counts, key=trend_counts.get)
        return {"total_score": total_score, "trend": max_trend, "trend_alignment": trend_counts, "timeframe_count": len(timeframes)}

    def _handle_time_resets(self, df: pd.DataFrame, i: int):
        idx = df.index[i]
        try:
            candle_day = idx.date()
        except AttributeError:
            candle_day = idx
        candle_week = idx.isocalendar()[1] if hasattr(idx, "isocalendar") else None
        if self._current_day is not None:
            try:
                if hasattr(candle_day, "__eq__") and candle_day != self._current_day:
                    self._current_day = candle_day
                    self.risk_manager.reset_daily()
                    self.risk_manager.consecutive_losses = 0
            except Exception:
                self._current_day = candle_day
        else:
            self._current_day = candle_day
        if self._current_week is not None and candle_week is not None:
            if candle_week != self._current_week:
                self._current_week = candle_week
                self.risk_manager.reset_weekly()
        else:
            self._current_week = candle_week
        if self.risk_manager.is_paused:
            self.risk_manager.is_paused = False

    def _compute_pnl(
        self, entry: float, exit_price: float, quantity: float, direction: str, commission: float
    ) -> Tuple[float, float]:
        gross = (exit_price - entry) * quantity if direction == "long" else (entry - exit_price) * quantity
        fees = entry * quantity * commission + exit_price * quantity * commission
        net = gross - fees
        pct = (exit_price - entry) / entry * 100 if direction == "long" else (entry - exit_price) / entry * 100
        return net, pct

    def _compute_metrics(self) -> Dict[str, Any]:
        total = len(self.trades)
        if total == 0:
            return {"total_trades": 0, "net_profit": 0}
        wins = [t for t in self.trades if t.get("pnl", 0) > 0]
        losses = [t for t in self.trades if t.get("pnl", 0) <= 0]
        win_rate = len(wins) / total * 100 if total > 0 else 0
        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
        net_profit = self.balance - self.initial_balance
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(365) if len(returns) > 1 and np.std(returns) > 0 else 0
        cum_max = np.maximum.accumulate(self.equity_curve)
        drawdowns = (cum_max - self.equity_curve) / cum_max * 100
        max_dd = np.max(drawdowns) if len(drawdowns) > 0 else 0
        avg_trade = net_profit / total
        avg_win = np.mean([t["pnl"] for t in wins]) if wins else 0
        avg_loss = np.mean([t["pnl"] for t in losses]) if losses else 0
        negative_returns = [r for r in returns if r < 0]
        sortino = np.mean(returns) / np.std(negative_returns) * np.sqrt(365) if negative_returns and np.std(negative_returns) > 0 else 0
        expectancy = (win_rate / 100 * avg_win) - ((1 - win_rate / 100) * abs(avg_loss))
        recovery_factor = abs(net_profit / max_dd) if max_dd > 0 else 0
        return {
            "total_trades": total,
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2),
            "net_profit": round(net_profit, 2),
            "total_return": round(net_profit / self.initial_balance * 100, 2),
            "max_drawdown": round(max_dd, 2),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "average_trade": round(avg_trade, 2),
            "average_win": round(avg_win, 2),
            "average_loss": round(avg_loss, 2),
            "expectancy": round(expectancy, 4),
            "recovery_factor": round(recovery_factor, 2),
            "final_balance": round(self.balance, 2),
            "avg_holding_period": "",
        }
