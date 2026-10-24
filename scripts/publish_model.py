"""Validate and publish versioned model artifacts."""

import argparse
import hashlib
import json
import re

from datetime import datetime, timezone
from pathlib import Path

from examples.model_lifecycle.train import (
    evaluate,
    load_model,
    make_dataset,
)

MAX_TEST_MSE = 0.001


def publish_model(model_path: Path, version: str, output_dir: Path):

    # 1. Validate version name
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", version):
        raise ValueError("Invalid model version")

    # 2. Load and validate the model
    model = load_model(model_path)

    # 3. Evaluate model quality
    _, _, test_x, test_y = make_dataset()
    test_mse = evaluate(model, test_x, test_y)

    if test_mse >= MAX_TEST_MSE:
        raise ValueError(
            f"Model rejected: MSE {test_mse} >= {MAX_TEST_MSE}"
        )

    # 4. Calculate model SHA-256
    model_bytes = model_path.read_bytes()
    model_sha256 = hashlib.sha256(model_bytes).hexdigest()

    # 5. Prevent overwriting existing versions
    version_dir = output_dir / version

    if version_dir.exists():
        raise FileExistsError(
            f"Model version already exists: {version}"
        )

    # 6. Create version directory
    output_dir.mkdir(parents=True, exist_ok=True)
    version_dir.mkdir(exist_ok=False)

    # 7. Save model artifact
    (version_dir / "model.json").write_bytes(model_bytes)

    # 8. Create metadata
    metadata = {
        "version": version,
        "format": model["format"],
        "dataset": "synthetic-linear-v1",
        "test_mse": test_mse,
        "max_test_mse": MAX_TEST_MSE,
        "sha256": model_sha256,
        "status": "validated_candidate",
        "input": {
            "features": model["feature_names"],
            "shape": "(n, 2)"
        },
        "output": {
            "type": "numeric prediction",
            "shape": "(n,)"
        },
        "published_at": datetime.now(timezone.utc).isoformat()
    }

    (version_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n"
    )

    return metadata


def main():
    parser = argparse.ArgumentParser(
        description="Publish a validated model version"
    )

    parser.add_argument(
        "--model-path",
        type=Path,
        required=True
    )

    parser.add_argument(
        "--version",
        required=True
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/models")
    )

    args = parser.parse_args()

    metadata = publish_model(
        args.model_path,
        args.version,
        args.output_dir
    )

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()