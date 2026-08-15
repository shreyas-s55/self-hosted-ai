#!/usr/bin/env bash

set -euo pipefail

STATE_DIR="/var/lib/self-hosted-ai"
LOG_FILE="/var/log/auto_gpu_setup.log"
SERVICE_NAME="self-hosted-ai-gpu-setup.service"
DRIVER_MARKER="${STATE_DIR}/gpu-driver-installed"
RUNTIME_MARKER="${STATE_DIR}/gpu-runtime-installed"
DEPLOY_MARKER="${STATE_DIR}/gpu-default-deploy-complete"

mkdir -p "${STATE_DIR}"

exec > >(tee -a "${LOG_FILE}")
exec 2>&1

echo "=================================================="
echo "Self Hosted AI GPU Automation"
echo "Time: $(date)"
echo "=================================================="

if [[ -f "${DEPLOY_MARKER}" ]]; then
    echo "GPU automation already completed."
    systemctl disable "${SERVICE_NAME}" || true
    exit 0
fi

if [[ ! -f "${DRIVER_MARKER}" ]]; then
    echo
    echo "Installing NVIDIA driver before reboot..."
    /opt/self-hosted-ai/terraform/scripts/install_gpu.sh
    touch "${DRIVER_MARKER}"

    echo
    echo "Rebooting to load the NVIDIA driver..."
    reboot
    exit 0
fi

systemctl start docker

if [[ ! -f "${RUNTIME_MARKER}" ]]; then
    echo
    echo "Installing NVIDIA container runtime after reboot..."
    /opt/self-hosted-ai/terraform/scripts/install_gpu_runtime.sh
    touch "${RUNTIME_MARKER}"
fi

echo
echo "Deploying default single-model stack..."
/opt/self-hosted-ai/deploy/scripts/deploy.sh
touch "${DEPLOY_MARKER}"

systemctl disable "${SERVICE_NAME}" || true

echo
echo "=================================================="
echo "GPU automation completed successfully"
echo "=================================================="