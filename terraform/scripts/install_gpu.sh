#!/usr/bin/env bash

set -euxo pipefail

LOG_FILE="/var/log/install_gpu.log"

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=================================================="
echo "Installing NVIDIA Driver"
echo "Started: $(date)"
echo "=================================================="

export DEBIAN_FRONTEND=noninteractive

#######################################################
# Update
#######################################################

apt-get update

#######################################################
# Install prerequisites
#######################################################

apt-get install -y \
    ubuntu-drivers-common

#######################################################
# Detect GPU
#######################################################

echo
echo "Detected GPU:"
echo

lspci | grep -i nvidia

echo
echo "Recommended Driver:"
echo

ubuntu-drivers devices

#######################################################
# Install Driver
#######################################################

ubuntu-drivers install

#######################################################
# Finished
#######################################################

echo
echo "=================================================="
echo "Driver installation completed."
echo
echo "A reboot is required."
echo
echo "Run:"
echo
echo "sudo reboot"
echo
echo "After reboot execute:"
echo
echo "sudo /opt/self-hosted-ai/terraform/scripts/install_gpu_runtime.sh"
echo "=================================================="