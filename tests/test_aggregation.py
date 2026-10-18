import json

import pytest

from pipelines.steps.db_update.run import collect_results


def test_collect_results_requires_exact_registered_image_set(tmp_path):
    first = tmp_path / "image-001"
    first.mkdir()
    (first / "inference.json").write_text(json.dumps({
        "experiment_id": "exp-1", "image_id": "image-001", "foreground_fraction": 0.5,
        "mean_intensity": 200.0, "model_sha256": "abc"
    }))
    assert collect_results(tmp_path, "exp-1", ["image-001"])[0]["image_id"] == "image-001"
    with pytest.raises(ValueError, match="missing or unexpected"):
        collect_results(tmp_path, "exp-1", ["image-001", "image-002"])
