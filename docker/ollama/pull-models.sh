#!/usr/bin/env bash
# Run once after 'docker compose up ollama' to pull required AI models.
# Total download: ~9 GB — run on a fast connection.
set -euo pipefail

CONTAINER=calorie-tracker-ollama-1

echo '==> Pulling gemma3:12b (text generation + NL parsing)...'
docker exec "$CONTAINER" ollama pull gemma3:12b

echo '==> Pulling qwen3-vl:8b (food photo vision recognition)...'
docker exec "$CONTAINER" ollama pull qwen3-vl:8b

echo '==> Pulling nomic-embed-text (semantic food search embeddings)...'
docker exec "$CONTAINER" ollama pull nomic-embed-text

echo '==> All models pulled successfully.'
docker exec "$CONTAINER" ollama list
