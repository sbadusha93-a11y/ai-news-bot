import numpy as np
import pandas as pd
from loguru import logger
from sklearn.preprocessing import StandardScaler

from src.config import settings
from src.ml.features import FeatureEngineer
from src.ml.models import MLModels


class MLPredictor:
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.models = MLModels(settings.ml_model_path)
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            self.models.load_all_models()
            self._loaded = True

    def _maybe_unload(self):
        if getattr(settings, 'railway_lite_mode', False):
            self.models.unload_models()
            self._loaded = False

    def predict(self, df: pd.DataFrame) -> dict:
        self._ensure_loaded()

        features = self.feature_engineer.create_features(df)
        if features.empty:
            return {
                "prediction": 0,
                "probability": 0.5,
                "confidence": 0,
                "models_used": 0,
            }

        feature_cols = [
            c for c in features.columns
            if c not in ("target", "symbol")
        ]
        X = features[feature_cols].iloc[[-1]].values

        scaler = self.models.load_model("scaler")
        if scaler:
            X = scaler.transform(X)

        avg_pred, avg_prob, confidence = self.models.get_ensemble_prediction(X)
        models_count = self.models.get_model_count()

        return {
            "prediction": float(avg_pred),
            "probability": float(avg_prob),
            "confidence": float(confidence),
            "models_used": models_count,
            "direction": "long" if avg_pred > 0.5 else "short" if avg_pred < 0.5 else "neutral",
        }
