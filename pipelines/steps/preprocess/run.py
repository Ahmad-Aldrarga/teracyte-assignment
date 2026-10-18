"""Starter preprocessing step. Local paths are a deliberate portability exercise."""

import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image


def otsu_threshold(pixels: np.ndarray) -> int:
    histogram = np.bincount(pixels.ravel(), minlength=256).astype(np.float64)
    count = np.cumsum(histogram)
    weighted = np.cumsum(histogram * np.arange(256))
    total = count[-1]
    between = np.zeros(256, dtype=np.float64)
    valid = (count > 0) & (count < total)
    between[valid] = (weighted[-1] * count[valid] - weighted[valid] * total) ** 2 / (
        count[valid] * (total - count[valid])
    )
    return int(np.argmax(between))


def preprocess_image(
    experiment_id: str, image_id: str, image_path: Path, mask_path: Path, output_path: Path
) -> dict:
    started = time.perf_counter()
    with Image.open(image_path) as source:
        grayscale = source.convert("L")
        # NOTE: Known memory bottleneck - loads full uncompressed array copies.
        # The Python list also holds one reference per pixel before NumPy copies it.
        pixels = np.array(list(grayscale.tobytes()), dtype=np.uint8).reshape(
            grayscale.height, grayscale.width
        )
    threshold = otsu_threshold(pixels)
    mask = np.where(pixels > threshold, 255, 0).astype(np.uint8)
    mask_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask).save(mask_path)
    metadata = {
        "experiment_id": experiment_id,
        "image_id": image_id,
        "mask_path": str(mask_path),
        "threshold": threshold,
        "width": int(mask.shape[1]),
        "height": int(mask.shape[0]),
        "foreground_pixels": int(np.count_nonzero(mask)),
        "duration_seconds": round(time.perf_counter() - started, 3),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an Otsu threshold mask")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--image-id", required=True)
    parser.add_argument("--image-path", type=Path, required=True)
    parser.add_argument("--mask-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(preprocess_image(args.experiment_id, args.image_id, args.image_path, args.mask_path, args.output)))


if __name__ == "__main__":
    main()
