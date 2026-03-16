#!/usr/bin/env bash

set -e

echo "Starting Uniforma deploy"

cd /opt/uniforma

echo "Pull latest code"
git pull origin main

echo "Building backend"
cd backend
python3 -m compileall app

echo "Building admin"
cd ../admin
npm install
npm run build

echo "Building frontend"
cd ../frontend
npm install
npm run build

echo "Restart backend (docker)"
cd ../backend
docker compose restart || true

echo "Restart admin (pm2)"
pm2 restart uniforma-admin || true

echo "Deploy finished"
