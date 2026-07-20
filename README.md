# Self-Hosted AI

A fully automated, self-hosted Open Source LLM platform on AWS.

## Architecture

```
config/config.yaml               ← Single source of truth
       │
       ├──→ tools/validate.py     ← Configuration validation
       │
       └──→ tools/generate.py     ← Generates deployment artifacts
               │
               ├──→ deploy/.env
               └──→ deploy/compose.generated.yaml
                          │
                          └──→ docker compose up
```

### Runtime Adapter

The platform uses a **runtime adapter** pattern to support multiple inference
engines. Each adapter translates the unified configuration into engine-specific
command-line arguments.

```
tools/lib/runtime/
├── __init__.py    ← Registry (get_runtime_adapter)
├── base.py        ← Abstract base class (RuntimeAdapter)
└── vllm.py        ← vLLM implementation (VLLMAdapter)
```

Currently supported runtimes:

| Runtime | Adapter        | Status        |
|---------|----------------|---------------|
| vLLM    | `VLLMAdapter`  | Supported     |

### Deployment Flow

The deployment script (`deploy/scripts/deploy.sh`) executes the following
steps in order:

1. **Validate** — `python3 tools/validate.py` checks `config/config.yaml`.
2. **Generate** — `python3 tools/generate.py` produces `deploy/.env` and
   `deploy/compose.generated.yaml`.
3. **Pull** — `docker compose pull` fetches the latest container images.
4. **Start** — `docker compose up -d --wait` launches all services and waits
   for the runtime health check (`GET /health`) to return HTTP 200.
5. **Status** — `docker compose ps` reports the final state.

## Goals

- Single EC2 deployment
- Terraform automation
- Docker Compose with generated configuration
- OpenAI-compatible API
- Open WebUI
- Low cost
- Easy to destroy and recreate

## Prerequisites

- AWS account with appropriate permissions
- Terraform installed locally
- SSH key pair

## Deployment

### 1. Provision Infrastructure

```bash
cd terraform
terraform apply
```

### 2. Install GPU Drivers

SSH to the instance and run:

```bash
sudo /opt/self-hosted-ai/terraform/scripts/install_gpu.sh
sudo reboot
```

After reboot:

```bash
sudo /opt/self-hosted-ai/terraform/scripts/install_gpu_runtime.sh
```

Verify GPU access:

```bash
docker run --rm --gpus all nvidia/cuda:13.0.1-base-ubuntu24.04 nvidia-smi
```

### 3. Deploy the Platform

```bash
cd /opt/self-hosted-ai
./deploy/scripts/deploy.sh
```

### 4. Verify

```bash
docker exec open-webui curl http://vllm:8000/v1/models
```

## Configuration

All configuration is managed in `config/config.yaml`.

### Tool Calling

Enable tool-calling support for compatible models:

```yaml
features:
  tool_calling:
    enabled: true
    parser: hermes
```

When enabled, the runtime adapter appends the appropriate flags. For vLLM
this adds `--enable-auto-tool-choice --tool-call-parser hermes`.

Set `enabled: false` to disable tool calling without removing the section.

## Adding a New Runtime

Adding a new inference engine requires three steps:

### 1. Create the adapter

Create `tools/lib/runtime/<engine>.py`:

```python
from lib.runtime.base import RuntimeAdapter

class MyEngineAdapter(RuntimeAdapter):

    @property
    def image(self) -> str:
        return "my-engine/image:latest"

    def build_command(self, config: dict) -> list[str]:
        model = config["model"]
        runtime = config["runtime"]
        return [
            "--model", model["name"],
            "--port", str(runtime["port"]),
        ]
```

### 2. Register it

In `tools/lib/runtime/__init__.py`, import and add to the registry:

```python
from lib.runtime.my_engine import MyEngineAdapter

_REGISTRY: dict[str, type[RuntimeAdapter]] = {
    "vllm": VLLMAdapter,
    "my_engine": MyEngineAdapter,
}
```

### 3. Update config

Set the engine in `config/config.yaml`:

```yaml
runtime:
  engine: my_engine
  port: 8000
```

Run `./deploy/scripts/deploy.sh` to deploy with the new runtime.

## Project Structure

```
config/
  config.yaml                   ← Project configuration
deploy/
  compose.yaml                  ← Original compose reference
  compose.generated.yaml        ← Generated compose (used by deploy)
  scripts/
    deploy.sh                   ← Deployment entry point
  caddy/
    Caddyfile
terraform/                      ← Infrastructure as code
tools/
  generate.py                   ← Artifact generation CLI
  validate.py                   ← Configuration validation CLI
  requirements.txt
  lib/
    __init__.py
    config_loader.py            ← YAML config loader
    compose_generator.py        ← Compose and .env generator
    validator.py                ← Config validation logic
    runtime/
      __init__.py               ← Runtime adapter registry
      base.py                   ← RuntimeAdapter abstract base class
      vllm.py                   ← vLLM adapter
```

