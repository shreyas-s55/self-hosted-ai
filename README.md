# Self AI

A fully automated, self-hosted Open Source LLM platform on AWS.

## Goals

- Single EC2 deployment
- Terraform automation
- Docker Compose
- OpenAI-compatible API
- Open WebUI
- Low cost
- Easy to destroy and recreate

## Status

🚧 Project under development


terraform apply

ssh to machine and execute 
sudo /opt/self-hosted-ai/terraform/scripts/install_gpu.sh
sudo reboot

sudo /opt/self-hosted-ai/terraform/scripts/install_gpu_runtime.sh

verification: docker run --rm --gpus all nvidia/cuda:13.0.1-base-ubuntu24.04 nvidia-smi


cd /opt/self-hosted-ai
./deploy/scripts/deploy.sh