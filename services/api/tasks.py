"""Celery tasks and result query shared with the API."""

import json
import os
import re
from pathlib import Path

import psycopg
from celery import Celery


celery_app = Celery(
    "experiment_api",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:16379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:16379/1"),
)


def read_results(experiment_id: str) -> list[dict]:
    postgres_url = os.getenv("POSTGRES_URL", "postgresql://starter:starter@localhost:15432/experiments")
    with psycopg.connect(postgres_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT image_id, foreground_fraction, mean_intensity, model_sha256
                FROM image_metrics WHERE experiment_id = %s ORDER BY image_id
            """, (experiment_id,))
            return [
                {"image_id": row[0], "foreground_fraction": row[1],
                 "mean_intensity": row[2], "model_sha256": row[3]}
                for row in cursor.fetchall()
            ]


@celery_app.task(name="exports.write_report")
def write_report(experiment_id: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", experiment_id):
        raise ValueError("invalid experiment_id")
    # Fixed local storage is sufficient for core tasks; object storage is optional.
    report_path = Path("data/objects/reports") / f"{experiment_id}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({"experiment_id": experiment_id, "results": read_results(experiment_id)}, indent=2) + "\n")
    return str(report_path)
