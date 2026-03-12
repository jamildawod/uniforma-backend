#!/usr/bin/env bash
set -euo pipefail

if [ ! -d /opt/uniforma/storage/images ]; then
  mkdir -p /opt/uniforma/storage/images
fi

if [ ! -d /opt/uniforma/data ]; then
  mkdir -p /opt/uniforma/data
fi

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
