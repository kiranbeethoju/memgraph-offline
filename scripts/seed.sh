#!/usr/bin/env bash
# Load the sample film graph and company graph into Alpha once.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HTTP="${DGRAPH_HTTP:-http://127.0.0.1:8080}"

echo "Waiting for Alpha at ${HTTP} ..."
ready=0
for _ in $(seq 1 90); do
  if curl -sf "${HTTP}/health" | grep -q '"status":"healthy"'; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo "Alpha did not become healthy at ${HTTP}" >&2
  exit 1
fi

existing="$(curl -sf -H "Content-Type: application/dql" -X POST "${HTTP}/query" \
  --data-binary '{ q(func: eq(title, "Inception")) { uid } }')"
if printf '%s' "$existing" | grep -q '"q":\[{'; then
  echo "Sample datasets are already loaded."
  exit 0
fi

echo "Applying schema ..."
curl -sf -H "Content-Type: application/rdf" -X POST "${HTTP}/alter" \
  --data-binary @"${ROOT}/data/schema.dql" >/dev/null

echo "Loading the film graph ..."
curl -sf -H "Content-Type: application/json" -X POST "${HTTP}/mutate?commitNow=true" \
  --data-binary @"${ROOT}/data/movies.json" >/dev/null

echo "Loading the company graph ..."
curl -sf -H "Content-Type: application/json" -X POST "${HTTP}/mutate?commitNow=true" \
  --data-binary @"${ROOT}/data/companies.json" >/dev/null

echo "Loaded 8 films and 3 companies."
