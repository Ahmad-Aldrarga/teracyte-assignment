import json
from pathlib import Path

import numpy as np
from PIL import Image

from pipelines.steps.preprocess.run import preprocess_image
from pipelines.steps.ml_infer.run import infer_image
from scripts.generate_mock_data import generate_data


def test_generator_creates_five_images_and_model(tmp_path):
    manifest = generate_data(tmp_path, width=64, height=48, model_bytes=1024)
    assert len(manifest["image_ids"]) == 5
    assert (tmp_path / "model" / "model.weights").stat().st_size == 1024
    assert all((tmp_path / "objects" / "raw" / f"{image_id}.png").exists() for image_id in manifest["image_ids"])


def test_steps_produce_joinable_results(tmp_path):
    raw = tmp_path / "raw.png"
    mask = tmp_path / "mask.png"
    pre = tmp_path / "preprocess.json"
    result = tmp_path / "inference.json"
    model = tmp_path / "model.weights"
    Image.fromarray(np.array([[0, 0, 255, 255], [0, 0, 255, 255]], dtype=np.uint8)).save(raw)
    model.write_bytes(b"model-seed")

    preprocess_image("exp-1", "image-1", raw, mask, pre)
    infer_image("exp-1", "image-1", raw, pre, model, result)

    metadata = json.loads(pre.read_text())
    metrics = json.loads(result.read_text())
    assert metadata["experiment_id"] == metrics["experiment_id"] == "exp-1"
    assert metadata["image_id"] == metrics["image_id"] == "image-1"
    assert metadata["foreground_pixels"] == 4
    assert metrics["foreground_fraction"] == 0.5
    assert Path(metadata["mask_path"]) == mask
