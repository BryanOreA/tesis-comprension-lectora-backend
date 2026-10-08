"""
Script para entrenar el modelo Random Forest con datos sintéticos.
Ejecuta: python -m app.ml.train_model
"""
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

MODEL_PATH = Path(__file__).parent / "random_forest_model.pkl"


def generate_synthetic_data(n_samples=2000):
    np.random.seed(42)
    percentage = np.random.uniform(0, 100, n_samples)
    avg_time = np.random.uniform(5, 60, n_samples)
    attempts = np.random.randint(1, 5, n_samples)
    help_used = np.random.randint(0, 10, n_samples)

    # Etiqueta basada en reglas + ruido
    labels = []
    for p, t, a, h in zip(percentage, avg_time, attempts, help_used):
        score = p - (t * 0.3) - (a * 3) - (h * 1.5)
        if score < 40:
            labels.append(0)  # En Inicio
        elif score < 70:
            labels.append(1)  # En Proceso
        else:
            labels.append(2)  # Satisfactorio

    X = pd.DataFrame({
        "percentage": percentage,
        "avg_time": avg_time,
        "attempts": attempts,
        "help_used": help_used
    })
    y = np.array(labels)
    return X, y


def train():
    print("Generando datos sintéticos...")
    X, y = generate_synthetic_data(2000)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Entrenando Random Forest...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Precisión: {acc:.4f}")
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred, target_names=["En Inicio", "En Proceso", "Satisfactorio"]))

    joblib.dump(model, MODEL_PATH)
    print(f"\nModelo guardado en: {MODEL_PATH}")


if __name__ == "__main__":
    train()