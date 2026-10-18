"""Supplied CPU training fixture; publication and promotion are candidate work."""

import argparse
import json
from pathlib import Path

import numpy as np


FEATURES = ["feature_a", "feature_b"]
FORMAT = "toy-linear-v1"
SEED = 2026


def make_dataset():
    """Return independent training and held-out arrays from a fixed seed."""
    rng = np.random.default_rng(SEED)
    features = rng.normal(size=(192, 2))
    targets = features @ np.array([1.5, -0.75]) + 2.0 + rng.normal(0, 0.01, 192)
    return features[:128], targets[:128], features[128:], targets[128:]


def fit(features: np.ndarray, targets: np.ndarray) -> dict:
    design = np.column_stack((features, np.ones(len(features))))
    weights = np.linalg.lstsq(design, targets, rcond=None)[0]
    return {
        "format": FORMAT,
        "feature_names": FEATURES.copy(),
        "coefficients": np.round(weights[:2], 8).tolist(),
        "intercept": round(float(weights[2]), 8),
    }


def load_model(path: Path) -> dict:
    """Load plain JSON, checking format and shape; no digest/approval policy."""
    model = json.loads(path.read_text())
    if not isinstance(model, dict) or model.get("format") != FORMAT:
        raise ValueError("unsupported model format")
    if model.get("feature_names") != FEATURES:
        raise ValueError("unsupported feature names or order")
    coefficients = np.asarray(model.get("coefficients"), dtype=float)
    intercept = np.asarray(model.get("intercept"), dtype=float)
    if coefficients.shape != (2,) or not np.isfinite(coefficients).all():
        raise ValueError("coefficients must contain two finite numbers")
    if intercept.shape != () or not np.isfinite(intercept):
        raise ValueError("intercept must be a finite scalar")
    return {**model, "coefficients": coefficients.tolist(), "intercept": float(intercept)}


def predict(model: dict, features) -> np.ndarray:
    values = np.asarray(features, dtype=float)
    if values.ndim != 2 or values.shape[1] != 2:
        raise ValueError("features must have shape (n, 2)")
    if not np.isfinite(values).all():
        raise ValueError("features must be finite")
    return values @ np.asarray(model["coefficients"]) + model["intercept"]


def evaluate(model: dict, features, targets) -> float:
    predictions = predict(model, features)
    expected = np.asarray(targets, dtype=float)
    if expected.shape != predictions.shape or not expected.size or not np.isfinite(expected).all():
        raise ValueError("targets must be a nonempty finite vector matching predictions")
    return round(float(np.mean((predictions - expected) ** 2)), 10)


def run_experiment(output_dir: Path) -> dict:
    train_x, train_y, test_x, test_y = make_dataset()
    model = fit(train_x, train_y)
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "model.json"
    model_path.write_text(json.dumps(model, indent=2, sort_keys=True, allow_nan=False) + "\n")
    reloaded = load_model(model_path)
    report = {
        "dataset": "synthetic-linear-v1",
        "seed": SEED,
        "train_rows": len(train_x),
        "test_rows": len(test_x),
        "test_mse": evaluate(reloaded, test_x, test_y),
        "baseline_test_mse": round(float(np.mean((test_y - train_y.mean()) ** 2)), 10),
    }
    (output_dir / "evaluation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and evaluate the supplied CPU toy model")
    parser.add_argument("--output-dir", type=Path, default=Path("data/model-lifecycle"))
    args = parser.parse_args()
    print(json.dumps(run_experiment(args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
