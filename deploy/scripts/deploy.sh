#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="/opt/self-hosted-ai"

usage() {
    cat <<'EOF'
Usage: deploy.sh [single|multi|multi-dedicated-gpu]

Modes:
  single                Deploy the default single-model runtime (default)
  multi                 Deploy all configured models sharing the available GPU(s)
  multi-dedicated-gpu   Deploy all configured models pinned one-per-GPU

Examples:
  sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh
  sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh multi
  sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh multi-dedicated-gpu
EOF
}

MODE="single"
GENERATE_ARGS=()

if [[ $# -gt 1 ]]; then
    usage
    exit 1
fi

if [[ $# -eq 1 ]]; then
    case "$1" in
        single|--single)
            MODE="single"
            ;;
        multi|--multi)
            MODE="multi"
            GENERATE_ARGS=(--profile multi)
            ;;
        multi-dedicated-gpu|--multi-dedicated-gpu|dedicated|--dedicated)
            MODE="multi-dedicated-gpu"
            GENERATE_ARGS=(--profile multi --pin-gpus)
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown mode: $1" >&2
            usage
            exit 1
            ;;
    esac
fi

echo "======================================="
echo "Deploying Self Hosted AI"
echo "Mode: ${MODE}"
echo "======================================="

cd "${PROJECT_ROOT}"

# Validate configuration
echo
echo "Validating configuration..."
python3 tools/validate.py

# Generate deployment artifacts
echo
echo "Generating deployment artifacts..."
python3 tools/generate.py "${GENERATE_ARGS[@]}"

cd deploy

# Stop previous mode cleanly before recreating services.
echo
echo "Stopping previous deployment..."
docker compose -f compose.generated.yaml --env-file .env down --remove-orphans

# Pull images
echo
echo "Pulling images..."
docker compose -f compose.generated.yaml --env-file .env pull

# Start services and wait for health
echo
echo "Starting services..."
docker compose -f compose.generated.yaml --env-file .env up -d \
    --build \
    --wait \
    --wait-timeout 600 \
    --remove-orphans

# Show status
echo
docker compose -f compose.generated.yaml --env-file .env ps

echo
echo "======================================="
echo "Deployment completed successfully"
echo "======================================="