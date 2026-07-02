import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from loguru import logger


class MLModels:
    def __init__(self, model_dir: str = "data/models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict] = {}

    def _load_metadata(self) -> Dict:
        meta_file = self.model_dir / "metadata.json"
        if meta_file.exists():
            with open(meta_file) as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        meta_file = self.model_dir / "metadata.json"
        with open(meta_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def save_model(self, name: str, model: Any, metrics: Optional[Dict] = None):
        path = self.model_dir / f"{name}.joblib"
        joblib.dump(model, path)
        self.models[name] = model
        self.metadata[name] = {
            "path": str(path),
            "metrics": metrics or {},
            "version": self.metadata.get(name, {}).get("version", 0) + 1,
        }
        self._save_metadata()
        logger.info(f"Model '{name}' saved to {path}")

    def load_model(self, name: str) -> Optional[Any]:
        if name in self.models:
            return self.models[name]

        path = self.model_dir / f"{name}.joblib"
        if path.exists():
            model = joblib.load(path)
            self.models[name] = model
            return model
        return None

    def load_all_models(self) -> Dict[str, Any]:
        self.metadata = self._load_metadata()
        for name in self.metadata:
            self.load_model(name)
        return self.models

    def get_ensemble_prediction(
        self, features: np.ndarray
    ) -> Tuple[float, float, float]:
        predictions = []
        probabilities = []

        for name, model in self.models.items():
            try:
                if hasattr(model, "predict_proba"):
                    proba = model.predict_proba(features)
                    if proba.shape[1] >= 2:
                        pred = model.predict(features)
                        predictions.append(pred)
                        probabilities.append(proba[:, 1])
                    else:
                        pred = model.predict(features)
                        predictions.append(pred)
                else:
                    pred = model.predict(features)
                    predictions.append(pred)
            except Exception as e:
                logger.warning(f"Model '{name}' prediction failed: {e}")

        if not predictions:
            return 0.0, 0.0, 0.0

        preds = np.array(predictions)
        avg_pred = np.mean(preds, axis=0)[0] if preds.ndim > 1 else float(np.mean(preds))

        if probabilities:
            avg_prob = float(np.mean([p[0] for p in probabilities]))
        else:
            avg_prob = abs(avg_pred)

        confidence = min(abs(avg_pred) * 100, 100) if len(predictions) > 0 else 0

        return avg_pred, avg_prob, confidence

    def list_models(self) -> List[str]:
        return list(self.metadata.keys())

    def get_model_count(self) -> int:
        return len(self.models)
