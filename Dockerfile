FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements-local.txt ./
COPY services/api/requirements.txt services/api/requirements.txt
COPY pipelines/steps/preprocess/requirements.txt pipelines/steps/preprocess/requirements.txt
COPY pipelines/steps/ml_infer/requirements.txt pipelines/steps/ml_infer/requirements.txt
COPY pipelines/steps/db_update/requirements.txt pipelines/steps/db_update/requirements.txt

RUN pip install --no-cache-dir -r requirements-local.txt

COPY services/ services/
COPY pipelines/ pipelines/
COPY examples/ examples/
COPY scripts/ scripts/

CMD ["python", "-m", "scripts.run_local"]