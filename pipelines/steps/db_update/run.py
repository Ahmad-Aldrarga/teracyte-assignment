"""Aggregate per-image JSON results into PostgreSQL and MongoDB."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def collect_results(results_dir: Path, experiment_id: str, image_ids: list[str]) -> list[dict]:
    results = [json.loads(path.read_text()) for path in sorted(results_dir.glob("*/inference.json"))]
    actual = [item.get("image_id") for item in results]
    if len(actual) != len(set(actual)) or set(actual) != set(image_ids):
        raise ValueError("missing or unexpected inference results")
    if any(item.get("experiment_id") != experiment_id for item in results):
        raise ValueError("inference result belongs to a different experiment")
    return results


def update_databases(experiment_id: str, results_dir: Path) -> int:
    import psycopg
    from pymongo import MongoClient

    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27018")
    postgres_url = os.getenv("POSTGRES_URL", "postgresql://starter:starter@localhost:15432/experiments")
    with MongoClient(mongo_url) as mongo:
        collection = mongo["experiments"]["experiments"]
        experiment = collection.find_one({"_id": experiment_id})
        if experiment is None:
            raise ValueError(f"unknown experiment: {experiment_id}")
        results = collect_results(results_dir, experiment_id, experiment["image_ids"])
        with psycopg.connect(postgres_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS image_metrics (
                        experiment_id TEXT NOT NULL,
                        image_id TEXT NOT NULL,
                        foreground_fraction DOUBLE PRECISION NOT NULL,
                        mean_intensity DOUBLE PRECISION NOT NULL,
                        model_sha256 TEXT NOT NULL,
                        PRIMARY KEY (experiment_id, image_id)
                    )
                """)
                for item in results:
                    cursor.execute("""
                        INSERT INTO image_metrics (
                            experiment_id, image_id, foreground_fraction, mean_intensity, model_sha256
                        ) VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (experiment_id, image_id) DO UPDATE SET
                            foreground_fraction = EXCLUDED.foreground_fraction,
                            mean_intensity = EXCLUDED.mean_intensity,
                            model_sha256 = EXCLUDED.model_sha256
                    """, (
                        experiment_id, item["image_id"], item["foreground_fraction"],
                        item["mean_intensity"], item["model_sha256"]
                    ))
        # The cross-database completion gap is an explicit candidate design exercise.
        collection.update_one({"_id": experiment_id}, {"$set": {
            "status": "COMPLETED", "completed_at": datetime.now(timezone.utc), "result_count": len(results)
        }})
        return len(results)


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist inference results")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--results-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({"experiment_id": args.experiment_id, "written": update_databases(args.experiment_id, args.results_dir)}))


if __name__ == "__main__":
    main()
