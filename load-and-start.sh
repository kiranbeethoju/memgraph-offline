#!/usr/bin/env bash
# Load the offline images and start Dgraph Zero, Alpha, and Ratel.
# Run this on the isolated Linux machine from the repository root.
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is not installed" >&2
  exit 1
fi

echo "Loading Dgraph and Ratel (linux/amd64)..."
docker load -i images/dgraph-offline-linux-amd64.tar

if docker compose version >/dev/null 2>&1; then
  docker compose up -d
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose up -d
else
  echo "Docker Compose is not available." >&2
  exit 1
fi

echo
echo "Ratel UI:     http://localhost:8000"
echo "Dgraph HTTP:  http://127.0.0.1:8080"
echo "Dgraph gRPC:  localhost:9080"
