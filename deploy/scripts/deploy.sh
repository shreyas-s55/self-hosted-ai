#!/usr/bin/env bash

set -euo pipefail

echo "======================================="
echo "Deploying Self Hosted AI"
echo "======================================="

cd /opt/self-hosted-ai

python3 - <<'PY'
import yaml
from pathlib import Path

config = yaml.safe_load(open("config/config.yaml"))

env = {
    "TZ": "UTC",
    "MODEL_NAME": config["model"]["name"],
    "MODEL_DTYPE": config["model"]["dtype"],
    "GPU_MEMORY_UTILIZATION": config["model"]["gpu_memory_utilization"],
    "MAX_MODEL_LEN": config["model"]["max_model_len"],
    "MODEL_CACHE_DIR": config["model"]["download_dir"],
    "HF_TOKEN": config["model"]["hf_token"],
    "RUNTIME_ENGINE": config["runtime"]["engine"],
    "RUNTIME_PORT": config["runtime"]["port"],
}

deploy_dir = Path("deploy")

with open(deploy_dir / ".env", "w") as f:
    for k, v in env.items():
        f.write(f"{k}={v}\n")
PY

cd deploy

docker compose pull

docker compose up -d

docker compose ps

echo
echo "======================================="
echo "Deployment completed successfully"
echo "======================================="