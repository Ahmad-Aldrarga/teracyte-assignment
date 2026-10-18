"""Mock inference with a real artifact dependency and deterministic metrics."""

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image


def infer_image(
    experiment_id: str,
    image_id: str,
    image_path: Path,
    preprocess_path: Path,
    model_path: Path,
    output_path: Path,
) -> dict:
    started = time.perf_counter()
    preprocessing = json.loads(preprocess_path.read_text())
    if (preprocessing["experiment_id"], preprocessing["image_id"]) != (experiment_id, image_id):
        raise ValueError("preprocessing metadata does not match requested image")
    weights = model_path.read_bytes()
    if not weights:
        raise ValueError("model artifact is empty")
    model_sha256 = hashlib.sha256(weights).hexdigest()
    with Image.open(image_path) as source, Image.open(preprocessing["mask_path"]) as mask_source:
        pixels = np.asarray(source.convert("L"), dtype=np.uint8)
        mask = np.asarray(mask_source.convert("L"), dtype=np.uint8) > 0
    if pixels.shape != mask.shape:
        raise ValueError("image and mask dimensions differ")
    foreground = int(np.count_nonzero(mask))
    result = {
        "experiment_id": experiment_id,
        "image_id": image_id,
        "foreground_fraction": round(foreground / mask.size, 6),
        "mean_intensity": round(float(pixels[mask].mean()), 3) if foreground else 0.0,
        "model_sha256": model_sha256,
        "duration_seconds": round(time.perf_counter() - started, 3),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run deterministic mock inference")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--image-path", type=Path, required=True)
    parser.add_argument("--preprocess", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(infer_image(args.experiment_id, args.image_id, args.image_path, args.preprocess, args.model_path, args.output)))


if __name__ == "__main__":
    main()
