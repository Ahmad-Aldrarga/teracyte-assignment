"""Minimal registration and reporting API for the assignment starter."""

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient

from .tasks import read_results, write_report


app = FastAPI(title="Experiment starter API")
ID_PATTERN = re.compile(r"[A-Za-z0-9_-]+\Z")


class ExperimentRequest(BaseModel):
    image_ids: list[str] = Field(min_length=1)


def experiments_collection():
    mongo = MongoClient(os.getenv("MONGO_URL", "mongodb://localhost:27018"))
    return mongo, mongo["experiments"]["experiments"]


@app.post("/experiments", status_code=201)
def register_experiment(request: ExperimentRequest):
    image_ids = request.image_ids
    if len(image_ids) != len(set(image_ids)) or any(not ID_PATTERN.fullmatch(value) for value in image_ids):
        raise HTTPException(status_code=422, detail="image_ids must be unique safe identifiers")
    # Fixed local storage is sufficient for core tasks; object storage is optional.
    missing = [image_id for image_id in image_ids if not (Path("data/objects/raw") / f"{image_id}.png").is_file()]
    if missing:
        raise HTTPException(status_code=404, detail=f"images unavailable: {missing}")
    experiment_id = uuid4().hex
    mongo, collection = experiments_collection()
    try:
        collection.insert_one({
            "_id": experiment_id, "image_ids": image_ids, "status": "PENDING",
            "created_at": datetime.now(timezone.utc)
        })
    finally:
        mongo.close()
    return {"experiment_id": experiment_id, "status": "PENDING", "image_ids": image_ids}


@app.get("/experiments/{experiment_id}/results")
def get_results(experiment_id: str):
    if not ID_PATTERN.fullmatch(experiment_id):
        raise HTTPException(status_code=422, detail="invalid experiment_id")
    mongo, collection = experiments_collection()
    try:
        document = collection.find_one({"_id": experiment_id})
    finally:
        mongo.close()
    if document is None:
        raise HTTPException(status_code=404, detail="unknown experiment")
    return {"experiment_id": experiment_id, "status": document["status"], "results": read_results(experiment_id) if document["status"] == "COMPLETED" else []}


@app.post("/experiments/{experiment_id}/exports", status_code=202)
def queue_export(experiment_id: str):
    if not ID_PATTERN.fullmatch(experiment_id):
        raise HTTPException(status_code=422, detail="invalid experiment_id")
    mongo, collection = experiments_collection()
    try:
        document = collection.find_one({"_id": experiment_id})
    finally:
        mongo.close()
    if document is None:
        raise HTTPException(status_code=404, detail="unknown experiment")
    if document["status"] != "COMPLETED":
        raise HTTPException(status_code=409, detail="experiment is not complete")
    task = write_report.delay(experiment_id)
    return {"task_id": task.id, "status": "QUEUED"}
