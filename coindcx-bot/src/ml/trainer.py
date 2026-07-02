import asyncio
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.config import settings
from src.ml.features import FeatureEngineer
from src.ml.models import MLModels


class MLTrainer:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models = MLModels(settings.ml_model_path)
        self.is_training = False

    async def train(
        self,
        dfs: Dict[str, pd.DataFrame],
        symbols: List[str],
    ) -> Dict[str, Any]:
        if self.is_training:
            return {"status": "already_training"}

        self.is_training = True
        try:
            all_features = []
            for symbol, df in dfs.items():
                features = self.feature_engineer.create_features(df)
                if not features.empty:
                    features["symbol"] = symbol
                    all_features.append(features)

            if not all_features:
                return {"status": "no_data"}

            combined = pd.concat(all_features, ignore_index=True)
            combined = combined.dropna()

            if len(combined) < 100:
                return {"status": "insufficient_data", "samples": len(combined)}

            X = combined[[c for c in combined.columns if c not in ("target", "symbol")]]
            y = combined["target"]
            y_class = (y > 0).astype(int)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y_class, test_size=0.2, random_state=42
            )

            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            results = {}

            rf = RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                random_state=42,
                n_jobs=-1,
            )
            rf.fit(X_train_scaled, y_train)
            rf_score = rf.score(X_test_scaled, y_test)
            self.models.save_model("random_forest", rf, {"accuracy": rf_score})
            results["random_forest"] = rf_score

            try:
                from xgboost import XGBClassifier
                xgb = XGBClassifier(
                    n_estimators=200,
                    max_depth=10,
                    learning_rate=0.05,
                    random_state=42,
                    n_jobs=-1,
                )
                xgb.fit(X_train_scaled, y_train)
                xgb_score = xgb.score(X_test_scaled, y_test)
                self.models.save_model("xgboost", xgb, {"accuracy": xgb_score})
                results["xgboost"] = xgb_score
            except ImportError:
                logger.warning("XGBoost not available")

            try:
                from lightgbm import LGBMClassifier
                lgb = LGBMClassifier(
                    n_estimators=200,
                    max_depth=10,
                    learning_rate=0.05,
                    random_state=42,
                    n_jobs=-1,
                )
                lgb.fit(X_train_scaled, y_train)
                lgb_score = lgb.score(X_test_scaled, y_test)
                self.models.save_model("lightgbm", lgb, {"accuracy": lgb_score})
                results["lightgbm"] = lgb_score
            except ImportError:
                logger.warning("LightGBM not available")

            try:
                from catboost import CatBoostClassifier
                cb = CatBoostClassifier(
                    iterations=200,
                    depth=10,
                    learning_rate=0.05,
                    random_state=42,
                    verbose=0,
                )
                cb.fit(X_train_scaled, y_train)
                cb_score = cb.score(X_test_scaled, y_test)
                self.models.save_model("catboost", cb, {"accuracy": cb_score})
                results["catboost"] = cb_score
            except ImportError:
                logger.warning("CatBoost not available")

            self.models.save_model("scaler", scaler)

            return {
                "status": "success",
                "samples": len(combined),
                "features": X.shape[1],
                "results": results,
            }

        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {"status": "error", "error": str(e)}
        finally:
            self.is_training = False
