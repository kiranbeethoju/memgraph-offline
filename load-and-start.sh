#!/usr/bin/env bash
# Load the offline images and start Memgraph plus Memgraph Lab.
# Run this on the isolated Linux machine from the repository root.
set -euo pipefail

cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is not installed" >&2
  exit 1
fi

echo "Loading Memgraph MAGE (linux/amd64)..."
docker load -i images/memgraph-mage-linux-amd64.tar

echo "Loading Memgraph Lab (linux/amd64)..."
docker load -i images/memgraph-lab-linux-amd64.tar

if docker compose version >/dev/null 2>&1; then
  docker compose up -d
elif command -v docker-compose >/dev/null 2>&1; then
  docker-compose up -d
else
  echo "Docker Compose is not available. Starting containers with docker run."
  docker volume create mg_lib >/dev/null
  docker run -d \
    --name memgraph-mage \
    --restart unless-stopped \
    -p 7687:7687 \
    -p 7444:7444 \
    -v mg_lib:/var/lib/memgraph \
    memgraph/memgraph-mage:latest
  docker run -d \
    --name memgraph-lab \
    --restart unless-stopped \
    --network host \
    -e QUICK_CONNECT_MG_HOST=127.0.0.1 \
    -e QUICK_CONNECT_MG_PORT=7687 \
    -e QUICK_CONNECT_MG_IS_ENCRYPTED=false \
    -e LOGIN_RESERVED_HOSTNAME_IS_ENABLED=true \
    memgraph/lab:latest
fi

echo
echo "Memgraph Bolt:  localhost:7687"
echo "Memgraph Lab:   http://localhost:3000"
