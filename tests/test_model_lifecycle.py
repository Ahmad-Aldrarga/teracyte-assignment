import json

import numpy as np
import pytest

from examples.model_lifecycle.train import evaluate, load_model, make_dataset, predict, run_experiment


def test_training_is_repeatable_and_reloaded_model_beats_baseline(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    report = run_experiment(first)
    assert run_experiment(second) == report
    assert (first / "model.json").read_bytes() == (second / "model.json").read_bytes()
    model = load_model(first / "model.json")
    _, _, features, targets = make_dataset()
    assert predict(model, features).shape == (64,)
    assert evaluate(model, features, targets) == report["test_mse"]
    assert report["test_mse"] < 0.001 < report["baseline_test_mse"]


def test_loader_and_prediction_enforce_the_feature_contract(tmp_path):
    run_experiment(tmp_path)
    path = tmp_path / "model.json"
    model = load_model(path)
    with pytest.raises(ValueError, match="shape"):
        predict(model, np.zeros((3, 1)))
    with pytest.raises(ValueError, match="finite"):
        predict(model, [[float("nan"), 1]])
    invalid = dict(model, coefficients=[1.0])
    path.write_text(json.dumps(invalid))
    with pytest.raises(ValueError, match="coefficients"):
        load_model(path)


def test_loaded_numeric_values_can_be_used_by_predict(tmp_path):
    run_experiment(tmp_path)
    path = tmp_path / "model.json"
    model = json.loads(path.read_text())
    model.update(coefficients=["1.0", "2.0"], intercept="3.0")
    path.write_text(json.dumps(model))
    assert predict(load_model(path), [[1.0, 1.0]]).tolist() == [6.0]
