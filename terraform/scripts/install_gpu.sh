#!/usr/bin/env bash

set -euxo pipefail

echo "========================================="
echo "GPU installation started"
echo "========================================="

export DEBIAN_FRONTEND=noninteractive

#########################################
# Install prerequisites
#########################################

apt-get update

apt-get install -y \
    build-essential \
    gcc \
    make \
    dkms \
    curl \
    wget \
    gnupg \
    lsb-release \
    ubuntu-drivers-common

#########################################
# Show detected GPU
#########################################

lspci | grep -i nvidia || true

echo "========================================="
echo "Recommended NVIDIA Drivers"
echo "========================================="

ubuntu-drivers devices

#########################################
# Install NVIDIA Driver
#########################################

ubuntu-drivers install

echo "========================================="
echo "GPU driver installation completed"
echo
echo "A reboot is required before continuing."
echo "========================================="