import itertools
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger


class StrategyOptimizer:
    def __init__(self):
        self.param_grid = {
            "rsi_period": [10, 14, 21],
            "macd_fast": [8, 12, 16],
            "macd_slow": [21, 26, 30],
            "atr_multiplier": [1.5, 2.0, 2.5, 3.0],
            "min_rr": [2.0, 2.5, 3.0, 3.5],
            "max_risk_per_trade": [0.5, 0.75, 1.0, 1.5],
        }

    async def optimize(
        self,
        df: pd.DataFrame,
        backtest_func: Callable,
        metric: str = "sharpe_ratio",
        max_combinations: int = 100,
        walk_forward_windows: int = 4,
        validation_split: float = 0.3,
    ) -> Dict[str, Any]:
        keys = list(self.param_grid.keys())
        values = list(self.param_grid.values())
        combinations = list(itertools.product(*values))

        if len(combinations) > max_combinations:
            indices = np.random.choice(
                len(combinations), max_combinations, replace=False
            )
            combinations = [combinations[i] for i in indices]

        total_len = len(df)
        window_size = total_len // walk_forward_windows
        if window_size < 500:
            walk_forward_windows = max(1, total_len // 500)
            window_size = total_len // walk_forward_windows

        oos_results = []
        for combo in combinations:
            params = dict(zip(keys, combo))
            oos_scores = []
            insample_scores = []

            for w in range(walk_forward_windows):
                start = w * window_size
                end = (w + 1) * window_size if w < walk_forward_windows - 1 else total_len
                split_point = int(end - (end - start) * validation_split)

                train_df = df.iloc[start:split_point].copy()
                test_df = df.iloc[split_point:end].copy()

                if len(train_df) < 200 or len(test_df) < 50:
                    continue

                try:
                    train_metrics = await backtest_func(train_df, params)
                    test_metrics = await backtest_func(test_df, params)
                    insample_scores.append(train_metrics.get(metric, 0) or 0)
                    oos_scores.append(test_metrics.get(metric, 0) or 0)
                except Exception as e:
                    logger.debug(f"Walk-forward failed for {params} window {w}: {e}")

            if oos_scores:
                avg_oos = np.mean(oos_scores)
                avg_is = np.mean(insample_scores) if insample_scores else 0
                decay = 1 - abs(avg_is - avg_oos) / max(abs(avg_is), 0.01) if avg_is != 0 else 0
                oos_results.append({
                    **params,
                    "avg_oos_sharpe": round(avg_oos, 4),
                    "avg_is_sharpe": round(avg_is, 4),
                    "walk_decay": round(decay, 4),
                    "final_score": round(avg_oos * (0.7 + 0.3 * decay), 4),
                    "windows": len(oos_scores),
                })

        if not oos_results:
            return {"error": "No valid walk-forward results"}

        results_df = pd.DataFrame(oos_results)
        score_col = "final_score"
        best_idx = results_df[score_col].idxmax()
        best_row = results_df.iloc[best_idx].to_dict()

        return {
            "best_params": {k: best_row[k] for k in keys if k in best_row},
            "best_metrics": {
                "final_score": best_row.get("final_score", 0),
                "avg_oos_sharpe": best_row.get("avg_oos_sharpe", 0),
                "avg_is_sharpe": best_row.get("avg_is_sharpe", 0),
                "walk_decay": best_row.get("walk_decay", 0),
            },
            "total_combinations": len(combinations),
            "valid_results": len(oos_results),
            "walk_forward_windows": walk_forward_windows,
        }

    async def random_search(
        self,
        df: pd.DataFrame,
        backtest_func: Callable,
        param_ranges: Dict[str, List],
        n_iter: int = 50,
    ) -> Dict[str, Any]:
        keys = list(param_ranges.keys())
        results = []

        for _ in range(n_iter):
            params = {}
            for k, v in param_ranges.items():
                if isinstance(v, list) and len(v) == 2:
                    if k.startswith("rsi") or k.endswith("period"):
                        params[k] = random.randint(v[0], v[1])
                    else:
                        params[k] = random.uniform(v[0], v[1])
                elif isinstance(v, list):
                    params[k] = random.choice(v)
                else:
                    params[k] = v
            try:
                metrics = await backtest_func(df, params)
                results.append({**params, **metrics})
            except Exception:
                continue

        if not results:
            return {"error": "No valid results"}
        results_df = pd.DataFrame(results)
        metric = "sharpe_ratio"
        best_idx = results_df[metric].idxmax() if metric in results_df else 0
        best = results_df.iloc[best_idx].to_dict()

        return {
            "best_params": {k: best[k] for k in keys if k in best},
            "best_metrics": {k: best[k] for k in results_df.columns if k not in keys},
            "total_trials": n_iter,
            "valid_results": len(results),
        }
