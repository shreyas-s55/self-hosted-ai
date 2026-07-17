#!/usr/bin/env bash

set -euo pipefail

echo "======================================="
echo "Deploying Self Hosted AI"
echo "======================================="

cd /opt/self-hosted-ai/deploy

docker compose pull

docker compose up -d

docker ps

echo "======================================="
echo "Deployment completed successfully"
echo "======================================="