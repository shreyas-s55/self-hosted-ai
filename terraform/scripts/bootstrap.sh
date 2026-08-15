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
    software-properties-common \
    python3 \
    python3-yaml

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

#########################################
# Clone Application Repository
#########################################

mkdir -p /opt

if [ ! -d "/opt/self-hosted-ai" ]; then
    git clone https://github.com/shreyas-s55/self-hosted-ai.git /opt/self-hosted-ai
else
    cd /opt/self-hosted-ai
    git pull
fi

#########################################
# Script Permissions
#########################################

chmod +x /opt/self-hosted-ai/terraform/scripts/install_gpu.sh

chmod +x /opt/self-hosted-ai/terraform/scripts/install_gpu_runtime.sh

chmod +x /opt/self-hosted-ai/terraform/scripts/auto_gpu_setup.sh

chmod +x /opt/self-hosted-ai/deploy/scripts/deploy.sh

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

#########################################
# Deployment Orchestration
#########################################

if [[ "${enable_gpu}" == "true" ]]; then

    echo
    echo "=================================================="
    echo "GPU instance detected."
    echo "Automated GPU provisioning enabled."
    echo "The instance will reboot once, verify GPU access,"
    echo "and then deploy the default single-model stack."
    echo
    echo "=================================================="

    install -m 0644 \
        /opt/self-hosted-ai/terraform/scripts/self-hosted-ai-gpu-setup.service \
        /etc/systemd/system/self-hosted-ai-gpu-setup.service

    systemctl daemon-reload
    systemctl enable self-hosted-ai-gpu-setup.service

else

    echo
    echo "=================================================="
    echo "CPU deployment selected."
    echo "=================================================="

fi

if [[ "${enable_gpu}" == "true" ]]; then
    touch "$MARKER_FILE"

    echo "=================================================="
    echo "Bootstrap completed successfully"
    echo "GPU automation will continue in the background."
    echo "Time: $(date)"
    echo "=================================================="

    systemctl start --no-block self-hosted-ai-gpu-setup.service
else
    /opt/self-hosted-ai/deploy/scripts/deploy.sh

    touch "$MARKER_FILE"

    echo "=================================================="
    echo "Bootstrap completed successfully"
    echo "Time: $(date)"
    echo "=================================================="
fi