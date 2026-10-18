"""Sequential baseline runner; Argo orchestration is an optional extension."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient

from scripts.generate_mock_data import generate_data


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the starter pipeline locally")
    parser.add_argument("--experiment-id", default="demo-local")
    args = parser.parse_args()
    data_dir = ROOT / "data"
    manifest_path = data_dir / "manifest.json"
    if not manifest_path.exists():
        generate_data(data_dir)
    manifest = json.loads(manifest_path.read_text())
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27018")
    with MongoClient(mongo_url) as mongo:
        mongo["experiments"]["experiments"].update_one(
            {"_id": args.experiment_id},
            {"$set": {"image_ids": manifest["image_ids"], "status": "PENDING", "created_at": datetime.now(timezone.utc)},
             "$unset": {"completed_at": "", "result_count": ""}},
            upsert=True,
        )
    work_dir = data_dir / "work" / args.experiment_id
    for image_id in manifest["image_ids"]:
        image_path = data_dir / "objects" / "raw" / f"{image_id}.png"
        image_work = work_dir / image_id
        preprocess = image_work / "preprocess.json"
        subprocess.run([
            sys.executable, "-m", "pipelines.steps.preprocess.run", "--experiment-id", args.experiment_id,
            "--image-id", image_id, "--image-path", str(image_path),
            "--mask-path", str(data_dir / "objects" / "masks" / args.experiment_id / f"{image_id}.png"),
            "--output", str(preprocess),
        ], cwd=ROOT, check=True)
        subprocess.run([
            sys.executable, "-m", "pipelines.steps.ml_infer.run", "--experiment-id", args.experiment_id,
            "--image-id", image_id, "--image-path", str(image_path),
            "--preprocess", str(preprocess), "--model-path", manifest["model_path"],
            "--output", str(image_work / "inference.json"),
        ], cwd=ROOT, check=True)
    subprocess.run([
        sys.executable, "-m", "pipelines.steps.db_update.run", "--experiment-id", args.experiment_id,
        "--results-dir", str(work_dir),
    ], cwd=ROOT, check=True)
    print(json.dumps({"experiment_id": args.experiment_id, "image_count": len(manifest["image_ids"]), "status": "COMPLETED"}))


if __name__ == "__main__":
    main()
