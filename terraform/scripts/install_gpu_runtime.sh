#!/usr/bin/env bash

set -euxo pipefail

LOG_FILE="/var/log/install_gpu_runtime.log"

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=================================================="
echo "Installing NVIDIA Container Toolkit"
echo "Started: $(date)"
echo "=================================================="

#######################################################
# Repository
#######################################################

curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
| gpg --dearmor \
-o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -fsSL \
https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
| sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#' \
> /etc/apt/sources.list.d/nvidia-container-toolkit.list

#######################################################
# Install Toolkit
#######################################################

apt-get update

apt-get install -y \
    nvidia-container-toolkit

#######################################################
# Configure Docker
#######################################################

nvidia-ctk runtime configure \
    --runtime=docker

systemctl restart docker

#######################################################
# Verification
#######################################################

echo
echo "Running GPU verification..."
echo

docker run --rm \
    --gpus all \
    nvidia/cuda:13.0.1-base-ubuntu24.04 \
    nvidia-smi

echo
echo "=================================================="
echo "GPU Runtime Ready"
echo "=================================================="