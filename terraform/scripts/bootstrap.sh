#!/bin/bash
set -euxo pipefail

LOG_FILE="/var/log/bootstrap.log"
MARKER_FILE="/var/lib/self-hosted-ai/bootstrap-complete"

mkdir -p /var/lib/self-hosted-ai

exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=================================================="
echo "Self Hosted AI Bootstrap Started"
echo "Time: $(date)"
echo "=================================================="

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get upgrade -y

apt-get install -y \
    ca-certificates \
    curl \
    git \
    unzip \
    gnupg \
    lsb-release \
    software-properties-common

###########################################################
# Docker
###########################################################

install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
| gpg --dearmor -o /etc/apt/keyrings/docker.gpg

chmod a+r /etc/apt/keyrings/docker.gpg

echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
> /etc/apt/sources.list.d/docker.list

apt-get update

apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin

systemctl enable docker
systemctl start docker

usermod -aG docker ubuntu

###########################################################
# AWS CLI
###########################################################

cd /tmp

curl -L \
https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip \
-o awscliv2.zip

unzip -q awscliv2.zip

./aws/install

rm -rf aws awscliv2.zip

###########################################################
# Cleanup
###########################################################

apt-get autoremove -y
apt-get autoclean

touch "$MARKER_FILE"

echo "=================================================="
echo "Bootstrap completed successfully"
echo "Time: $(date)"
echo "=================================================="