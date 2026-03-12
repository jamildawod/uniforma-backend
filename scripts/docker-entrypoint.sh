#!/usr/bin/env bash
set -euo pipefail

mkdir -p /opt/uniforma/storage/images
mkdir -p /opt/uniforma/data

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
