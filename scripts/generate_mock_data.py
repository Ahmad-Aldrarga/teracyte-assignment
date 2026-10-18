"""Generate reproducible camera images and an expendable model artifact."""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def generate_data(root: Path, width: int = 3072, height: int = 2048, model_bytes: int = 50 * 1024 * 1024) -> dict:
    if width < 1 or height < 1 or model_bytes < 1:
        raise ValueError("width, height and model size must be positive")
    raw_dir = root / "objects" / "raw"
    model_dir = root / "model"
    raw_dir.mkdir(parents=True, exist_ok=True)
    model_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(2026)
    image_ids = []
    x = np.linspace(0, 255, width, dtype=np.uint8)
    for number in range(1, 6):
        image_id = f"image-{number:03d}"
        image_ids.append(image_id)
        noise = rng.integers(0, 60, size=(height, width), dtype=np.uint8)
        pixels = (x[None, :].astype(np.uint16) + noise.astype(np.uint16) + number * 11) % 256
        Image.fromarray(pixels.astype(np.uint8)).save(raw_dir / f"{image_id}.png")
    model_path = model_dir / "model.weights"
    with model_path.open("wb") as model:
        block = b"mock-model-artifact-v1\n".ljust(1024 * 1024, b".")
        whole, remainder = divmod(model_bytes, len(block))
        for _ in range(whole):
            model.write(block)
        model.write(block[:remainder])
    manifest = {"image_ids": image_ids, "model_path": str(model_path), "width": width, "height": height}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate five sample images and a model")
    parser.add_argument("--root", type=Path, default=Path("data"))
    parser.add_argument("--width", type=int, default=3072)
    parser.add_argument("--height", type=int, default=2048)
    parser.add_argument("--model-mb", type=int, default=50)
    args = parser.parse_args()
    print(json.dumps(generate_data(args.root, args.width, args.height, args.model_mb * 1024 * 1024)))


if __name__ == "__main__":
    main()
