import itertools
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
    ) -> Dict[str, Any]:
        keys = list(self.param_grid.keys())
        values = list(self.param_grid.values())
        combinations = list(itertools.product(*values))

        if len(combinations) > max_combinations:
            indices = np.random.choice(
                len(combinations), max_combinations, replace=False
            )
            combinations = [combinations[i] for i in indices]

        results = []
        for combo in combinations:
            params = dict(zip(keys, combo))
            try:
                metrics = await backtest_func(df, params)
                results.append({**params, **metrics})
            except Exception as e:
                logger.warning(f"Optimization failed for {params}: {e}")

        if not results:
            return {"error": "No valid results"}

        results_df = pd.DataFrame(results)
        best_idx = results_df[metric].idxmax() if metric in results_df else 0
        best_params = results_df.iloc[best_idx].to_dict()

        return {
            "best_params": {
                k: best_params[k] for k in keys if k in best_params
            },
            "best_metrics": {
                k: best_params[k]
                for k in results_df.columns
                if k not in keys
            },
            "total_combinations": len(combinations),
            "valid_results": len(results),
        }
