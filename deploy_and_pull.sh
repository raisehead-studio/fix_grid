#!/bin/bash
set -e

echo "Starting deployment..."

docker compose down
git pull origin main
docker compose up -d --build

echo "Deployment complete!"
