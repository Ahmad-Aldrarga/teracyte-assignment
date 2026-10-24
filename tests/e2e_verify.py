import subprocess
import time
import uuid
from pathlib import Path
import os
import psycopg
import hashlib

from pymongo import MongoClient




ROOT = Path(__file__).resolve().parents[1]

def verify_model_sha256(experiment_id, expected_sha):

    postgres_url = os.getenv(
        "POSTGRES_URL",
        "postgresql://starter:starter@localhost:15432/experiments"
    )

    with psycopg.connect(postgres_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT image_id, model_sha256
                FROM image_metrics
                WHERE experiment_id = %s
                """,
                (experiment_id,)
            )

            rows = cursor.fetchall()

    if len(rows) != 5:
        raise AssertionError(
            f"Expected 5 rows, got {len(rows)}"
        )

    for image_id, actual_sha in rows:
        if actual_sha != expected_sha:
            raise AssertionError(
                f"SHA-256 mismatch for {image_id}: "
                f"expected {expected_sha}, got {actual_sha}"
            )

    print(f"Model SHA-256 verification: PASS - {expected_sha}")
def verify_mongo(experiment_id):
    mongo_url = os.getenv(
        "MONGO_URL",
        "mongodb://localhost:27018"
    )

    with MongoClient(mongo_url) as client:
        collection = client["experiments"]["experiments"]

        experiment = collection.find_one({
            "_id": experiment_id
        })

    assert experiment is not None, (
        f"Experiment {experiment_id} not found"
    )

    assert experiment["status"] == "COMPLETED", (
        f"Unexpected status: {experiment['status']}"
    )

    assert experiment["result_count"] == 5, (
        f"Expected 5 results, got {experiment['result_count']}"
    )

    expected_ids = [
        "image-001",
        "image-002",
        "image-003",
        "image-004",
        "image-005",
    ]

    assert sorted(experiment["image_ids"]) == expected_ids, (
        "MongoDB image IDs do not match expected IDs"
    )

    print("MongoDB verification: PASS - COMPLETED, 5 results")

def verify_postgres(experiment_id):
    postgres_url = os.getenv(
        "POSTGRES_URL",
        "postgresql://starter:starter@localhost:15432/experiments"
    )

    with psycopg.connect(postgres_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT image_id
                FROM image_metrics
                WHERE experiment_id = %s
                ORDER BY image_id
                """,
                (experiment_id,)
            )

            rows = cursor.fetchall()

    actual_ids = [row[0] for row in rows]

    expected_ids = [
        "image-001",
        "image-002",
        "image-003",
        "image-004",
        "image-005",
    ]

    assert len(rows) == 5, (
        f"Expected 5 rows, got {len(rows)}"
    )

    assert actual_ids == expected_ids, (
        f"Unexpected image IDs: {actual_ids}"
    )

    print("PostgreSQL verification: PASS - 5 images")

def main():
    # Create a unique experiment ID
    experiment_id = f"e2e-{uuid.uuid4().hex}"

    # Ensure fixtures exist before verification and timing.
    data_dir = ROOT / "data"
    required_files = [
        data_dir / "manifest.json",
        data_dir / "model" / "model.weights",
        *[
            data_dir / "objects" / "raw" / f"image-{i:03d}.png"
            for i in range(1, 6)
        ],
    ]
    if not all(file.is_file() for file in required_files):
        subprocess.run(
            ["python", "-m", "scripts.generate_mock_data", "--root", "data"],
            cwd=ROOT,
            check=True,
        )

    # Calculate expected model checksum before running the analysis
    model_path = ROOT / "data" / "model" / "model.weights"

    sha256 = hashlib.sha256()

    with model_path.open("rb") as model_file:
        for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
            sha256.update(chunk)

    expected_sha = os.getenv(
        "E2E_EXPECTED_SHA256",
        sha256.hexdigest()
    )
    print(f"Starting experiment: {experiment_id}", flush=True)

    # Start databases before measuring analysis time
    subprocess.run(
        ["docker", "compose", "up", "-d", "--wait", "postgres", "mongo", "redis"],
        cwd=ROOT,
        check=True,
    )

    # Unique container name for cleanup on timeout
    container_name = f"e2e-analysis-{uuid.uuid4().hex[:12]}"

    command = [
        "docker", "compose", "run",
        "--rm",
        "--no-deps",
        "--name", container_name,
        "analysis",
        "python", "-m", "scripts.run_local",
        "--experiment-id", experiment_id,
    ]

    # Measure analysis execution time
    start = time.monotonic()

    try:
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
            timeout=180,
        )

    except subprocess.TimeoutExpired:
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True,
            check=False,
        )
        raise SystemExit("FAIL: Analysis exceeded 180 seconds")

    duration = time.monotonic() - start

    print(f"Analysis duration: {duration:.2f} seconds")

    if duration > 180:
        raise SystemExit("FAIL: Analysis exceeded 180 seconds")

    # Verify database records and model checksum
    verify_postgres(experiment_id)
    verify_mongo(experiment_id)
    verify_model_sha256(experiment_id, expected_sha)
    print("E2E checks passed: PostgreSQL, MongoDB and SHA-256")


if __name__ == "__main__":
    main()