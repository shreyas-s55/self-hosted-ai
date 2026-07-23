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

### Deployment Modes

| Mode | Flag | Description |
|------|------|-------------|
| `single` | `--profile single` | One runtime serving the default model |
| `multi` | `--profile multi` | One runtime per deployment, all sharing the GPU |
| `multi` + GPU pinning | `--profile multi --pin-gpus` | Each runtime pinned to a dedicated GPU (multi-GPU instances) |

### Intelligent Routing

The gateway routes requests automatically when `model="auto"`:

```
Client  →  Gateway  →  RoutingService  →  Classifier  →  Deployment
                                              │
                                    ┌─────────┼──────────┐
                                  coder   reasoning    chat (default)
```

- **coder** — coding keywords detected (Python, FastAPI, SQL, Docker, Terraform, …)
- **reasoning** — logic/math keywords detected (prove, theorem, equation, …)
- **chat** — fallback default

Explicit model names (`chat`, `coder`, `reasoning`) bypass the classifier and route directly.

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

**Single model** (default — one model, one GPU):

```bash
sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh
```

**Multi model** (three models sharing one GPU, e.g. g6.xlarge):

```bash
sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh multi
```

**Multi model with dedicated GPUs** (one GPU per model, e.g. g6.12xlarge):

```bash
sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh multi-dedicated-gpu
```

### 4. Verify

Get your API key:

```bash
grep GATEWAY_API_KEY deploy/compose.generated.yaml
```

Check all deployments are healthy:

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/health
```

List available models:

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/v1/models
```

Test automatic routing:

```bash
# Routes to coder deployment
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Write a FastAPI endpoint that lists S3 buckets"}]}'

# Routes to reasoning deployment
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Prove that the square root of 2 is irrational"}]}'

# Explicit routing
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"coder","messages":[{"role":"user","content":"Hello"}]}'
```

Watch routing decisions in gateway logs:

```bash
sudo docker logs gateway --follow | python3 -m json.tool
```

Open WebUI in this deployment is configured to use the gateway's OpenAI-compatible
API only. The Ollama integration is disabled by default, so the UI should not
attempt to contact `host.docker.internal:11434`.

## Configuration

All configuration is managed in `config/config.yaml`.

### Deployments

```yaml
deployments:
  chat:
    runtime: vllm
    repository: Qwen/Qwen2.5-1.5B-Instruct
    default: true
    parameters:
      dtype: auto
      enforce_eager: true
      gpu_memory_utilization: 0.27
      max_model_len: 8192

  coder:
    runtime: vllm
    repository: Qwen/Qwen2.5-Coder-1.5B-Instruct
    parameters:
      dtype: auto
      enforce_eager: true
      gpu_memory_utilization: 0.27
      max_model_len: 8192

  reasoning:
    runtime: vllm
    repository: deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
    parameters:
      dtype: auto
      enforce_eager: true
      gpu_memory_utilization: 0.27
      max_model_len: 8192
```

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

