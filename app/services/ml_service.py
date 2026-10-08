import joblib
import numpy as np
from pathlib import Path
from typing import Optional

MODEL_PATH = Path(__file__).parent.parent / "ml" / "random_forest_model.pkl"

_model = None


def load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    return _model


def classify_level(percentage: float, avg_time: float, attempts: int, help_used: int) -> str:
    """
    Clasifica el nivel de comprensión lectora.
    Si el modelo no está entrenado, usa reglas heurísticas.
    """
    model = load_model()

    if model is not None:
        features = np.array([[percentage, avg_time, attempts, help_used]])
        prediction = model.predict(features)[0]
        return ["En Inicio", "En Proceso", "Satisfactorio"][prediction]

    # Fallback heurístico
    if percentage < 50:
        return "En Inicio"
    elif percentage < 75:
        return "En Proceso"
    return "Satisfactorio"