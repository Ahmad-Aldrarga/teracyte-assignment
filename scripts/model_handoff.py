"""Load and validate the selected model artifact."""

import hashlib
import json
import re
from pathlib import Path

from examples.model_lifecycle.train import load_model


ROOT = Path(__file__).resolve().parents[1]


def resolve_selected_model(
    config_path: Path,
    models_dir: Path,
):
    # 1. Read selected version from configuration
    config = json.loads(config_path.read_text())
    version = config.get("selected_version")

    if not isinstance(version, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_-]*", version
    ):
        raise ValueError("Invalid selected model version")

    # 2. Locate model and metadata
    version_dir = models_dir / version
    model_path = version_dir / "model.json"
    metadata_path = version_dir / "metadata.json"

    # 3. Read metadata
    metadata = json.loads(metadata_path.read_text())

    if metadata.get("version") != version:
        raise ValueError("Model version mismatch")

    if metadata.get("status") != "validated_candidate":
        raise ValueError("Model is not validated")

    # 4. Validate model structure
    model = load_model(model_path)

    if metadata.get("format") != model["format"]:
        raise ValueError("Model format mismatch")

    # 5. Validate SHA-256
    expected_sha = metadata.get("sha256")

    if not isinstance(expected_sha, str) or not re.fullmatch(
        r"[0-9a-f]{64}", expected_sha
    ):
        raise ValueError("Invalid model SHA-256 metadata")

    actual_sha = hashlib.sha256(
        model_path.read_bytes()
    ).hexdigest()

    if actual_sha != expected_sha:
        raise ValueError("Model SHA-256 mismatch")

    return model_path, actual_sha


def main():
    config_path = ROOT / "config" / "selected_model.json"
    models_dir = ROOT / "data" / "models"

    model_path, model_sha = resolve_selected_model(
        config_path,
        models_dir,
    )

    print("Model selection: PASS")
    print("Selected model:", model_path)
    print("Model SHA-256:", model_sha)


if __name__ == "__main__":
    main()