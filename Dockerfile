# Backend API (FastAPI). Installs the package + deps, runs migrations, then serves.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

COPY . .
RUN pip install .

EXPOSE 8000
# Apply DB migrations, then start the server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
