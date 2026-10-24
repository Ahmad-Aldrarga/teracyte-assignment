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


def test_selected_model_is_compatible_with_analysis(tmp_path):
    from hashlib import sha256

    from PIL import Image

    from pipelines.steps.ml_infer.run import infer_image
    from scripts.model_handoff import resolve_selected_model

    # 1. Train a model in an isolated directory.
    model_dir = tmp_path / "models" / "v1"
    run_experiment(model_dir)

    model_path = model_dir / "model.json"
    model_sha = sha256(model_path.read_bytes()).hexdigest()

    # 2. Create publication metadata.
    metadata = {
        "version": "v1",
        "status": "validated_candidate",
        "format": "toy-linear-v1",
        "sha256": model_sha,
    }
    (model_dir / "metadata.json").write_text(
        json.dumps(metadata)
    )

    # 3. Select the model through configuration.
    config_path = tmp_path / "selected_model.json"
    config_path.write_text(
        json.dumps({"selected_version": "v1"})
    )

    selected_path, selected_sha = resolve_selected_model(
        config_path,
        tmp_path / "models",
    )

    assert selected_path == model_path
    assert selected_sha == model_sha

    # 4. Prepare a small image and mask for Analysis.
    image_path = tmp_path / "image.png"
    mask_path = tmp_path / "mask.png"

    Image.fromarray(
        np.full((8, 8), 180, dtype=np.uint8)
    ).save(image_path)

    Image.fromarray(
        np.full((8, 8), 255, dtype=np.uint8)
    ).save(mask_path)

    preprocess_path = tmp_path / "preprocess.json"
    preprocess_path.write_text(json.dumps({
        "experiment_id": "compat-test",
        "image_id": "image-001",
        "mask_path": str(mask_path),
    }))

    # 5. Run the actual Analysis consumer.
    output_path = tmp_path / "result.json"

    result = infer_image(
        "compat-test",
        "image-001",
        image_path,
        preprocess_path,
        selected_path,
        output_path,
    )

    assert result["model_sha256"] == selected_sha
    assert result["foreground_fraction"] == 1.0
    assert result["mean_intensity"] == 180.0
    assert output_path.is_file()

    # 6. Verify that tampering is rejected.
    model_path.write_bytes(model_path.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        resolve_selected_model(
            config_path,
            tmp_path / "models",
        )
