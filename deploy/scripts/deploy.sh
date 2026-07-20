#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="/opt/self-hosted-ai"

echo "======================================="
echo "Deploying Self Hosted AI"
echo "======================================="

cd "${PROJECT_ROOT}"

# Validate configuration
echo
echo "Validating configuration..."
python3 tools/validate.py

# Generate deployment artifacts
echo
echo "Generating deployment artifacts..."
python3 tools/generate.py

cd deploy

# Pull images
echo
echo "Pulling images..."
docker compose -f compose.generated.yaml pull

# Start services and wait for health
echo
echo "Starting services..."
docker compose -f compose.generated.yaml up -d \
    --wait \
    --wait-timeout 600 \
    --remove-orphans

# Show status
echo
docker compose -f compose.generated.yaml ps

echo
echo "======================================="
echo "Deployment completed successfully"
echo "======================================="