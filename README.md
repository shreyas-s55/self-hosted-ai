# Self-Hosted AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/shreyas-s55/self-hosted-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/shreyas-s55/self-hosted-ai/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Terraform](https://img.shields.io/badge/terraform-1.9+-purple.svg)](https://www.terraform.io/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A fully automated, self-hosted open-source LLM platform on AWS. Provision a GPU instance, deploy one or more models behind an OpenAI-compatible gateway, and tear it all down when you're done — driven by a single config file.

> **Highlights**
> - One config file drives everything: infrastructure, runtime, and routing
> - OpenAI-compatible API — works with any agent or client without modification
> - Intelligent automatic model routing (`model="auto"`)
> - Ephemeral by design — cheap to run, cheap to destroy
> - Production-grade gateway: auth, structured logging, health checks, request IDs

---

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment Modes](#deployment-modes)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Agent Integration](#agent-integration)
- [Adding a New Runtime](#adding-a-new-runtime)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

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

### Stack

| Component | Technology | Port |
|-----------|-----------|------|
| Inference runtime | [vLLM](https://github.com/vllm-project/vllm) | 8000 (internal) |
| AI Gateway | FastAPI (custom) | 9000 |
| Web UI | [Open WebUI](https://github.com/open-webui/open-webui) | 8080 (internal) |
| Reverse proxy | [Caddy](https://caddyserver.com/) | 80 |
| Infrastructure | Terraform + AWS EC2 | — |

### Intelligent Routing

When clients send `model="auto"`, the gateway classifies the request and routes to the best deployment:

```
Client  →  Gateway  →  RoutingService  →  Classifier  →  Deployment
                                              │
                                    ┌─────────┼──────────┐
                                  coder   reasoning    chat (default)
```

| Route | Trigger |
|-------|---------|
| `coder` | Coding keywords detected (Python, SQL, Docker, Terraform, …) |
| `reasoning` | Logic/math keywords detected (prove, theorem, equation, …) |
| `chat` | Fallback default |

Explicit model names (`chat`, `coder`, `reasoning`) bypass the classifier entirely.

### Runtime Adapter Pattern

The platform abstracts inference engines through a `RuntimeAdapter` interface. Adding a new engine requires implementing one class.

```
tools/lib/runtime/
├── __init__.py    ← Registry (get_runtime_adapter)
├── base.py        ← Abstract base class (RuntimeAdapter)
└── vllm.py        ← vLLM implementation (VLLMAdapter)
```

| Runtime | Status |
|---------|--------|
| vLLM | ✅ Supported |
| SGLang | 🔜 Planned |
| llama.cpp | 🔜 Planned |
| Ollama | 🔜 Planned |

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| AWS account | Permissions: VPC, EC2, IAM |
| Terraform ≥ 1.9 | [Install guide](https://developer.hashicorp.com/terraform/install) |
| SSH key pair | Existing AWS key pair name |
| Python 3.12+ | For running tools locally |
| HuggingFace account | Token required for gated models |

---

## Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/shreyas-s55/self-hosted-ai.git
cd self-hosted-ai
```

Edit `config/config.yaml` to set your model and HuggingFace token:

```yaml
deployments:
  chat:
    runtime: vllm
    repository: Qwen/Qwen3-4B
    default: true
    parameters:
      dtype: auto
      gpu_memory_utilization: 0.95
      max_model_len: 32768

huggingface:
  token: "hf_your_token_here"
```

### 2. Configure Terraform

Copy and edit the variables file:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
aws_region    = "us-east-1"
instance_type = "g6.xlarge"   # g5.2xlarge, g6.xlarge, g6.12xlarge, etc.
enable_gpu    = true
```

### 3. Deploy infrastructure

```bash
terraform init
terraform apply
```

Terraform provisions the EC2 instance and runs the bootstrap script automatically. For GPU instances, the instance installs NVIDIA drivers, reboots once, installs the NVIDIA container runtime, and launches the full stack.

### 4. Watch bootstrap progress

```bash
# Get the instance IP
terraform output

# SSH and follow the log
ssh -i ~/.ssh/your-key.pem ubuntu@<INSTANCE_IP>
sudo tail -f /var/log/auto_gpu_setup.log
```

Or inspect the systemd service directly:

```bash
sudo systemctl status self-hosted-ai-gpu-setup.service --no-pager
sudo journalctl -u self-hosted-ai-gpu-setup.service -n 100 -f
```

### 5. Verify

```bash
# Get your auto-generated API key
grep GATEWAY_API_KEY /opt/self-hosted-ai/deploy/compose.generated.yaml

export TOKEN=<your-api-key>

# Health check
curl -H "Authorization: Bearer $TOKEN" http://<INSTANCE_IP>:9000/health

# List models
curl -H "Authorization: Bearer $TOKEN" http://<INSTANCE_IP>:9000/v1/models

# Chat completion
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     http://<INSTANCE_IP>:9000/v1/chat/completions \
     -d '{"model":"chat","messages":[{"role":"user","content":"Hello"}]}'
```

### 6. Destroy when done

```bash
cd terraform
terraform destroy
```

---

## Deployment Modes

| Mode | Command | Description |
|------|---------|-------------|
| Single (default) | `deploy.sh` | One runtime serving the default model |
| Multi | `deploy.sh multi` | All configured deployments share the GPU |
| Multi dedicated GPU | `deploy.sh multi-dedicated-gpu` | One GPU per deployment (multi-GPU instances) |

```bash
# Single model (default)
sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh

# Multiple models sharing one GPU (e.g. g6.xlarge)
sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh multi

# Multiple models, one GPU each (e.g. g6.12xlarge)
sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh multi-dedicated-gpu
```

### Deployment flow

Each invocation of `deploy.sh` runs these steps in order:

1. **Validate** — `python3 tools/validate.py` checks `config/config.yaml`
2. **Generate** — `python3 tools/generate.py` produces `deploy/.env` and `deploy/compose.generated.yaml`
3. **Stop** — gracefully stops the previous deployment
4. **Pull** — fetches latest container images
5. **Start** — `docker compose up -d --wait` waits for health checks
6. **Status** — reports final service state

---

## Configuration

All configuration lives in [`config/config.yaml`](config/config.yaml).

### Full reference

```yaml
project:
  name: self-hosted-ai
  environment: dev

aws:
  region: us-east-1

instance:
  type: g6.xlarge
  spot: false
  disk_size_gb: 80

runtime:
  engine: vllm       # vllm | sglang | llamacpp | ollama
  port: 8000

deployments:
  chat:
    runtime: vllm
    repository: Qwen/Qwen3-4B    # any HuggingFace model ID
    default: true                # serves as model="auto" fallback
    parameters:
      dtype: auto
      enforce_eager: true
      gpu_memory_utilization: 0.95
      max_model_len: 32768

  # Uncomment to enable multi-model mode:
  # coder:
  #   runtime: vllm
  #   repository: Qwen/Qwen2.5-Coder-1.5B-Instruct
  #   parameters:
  #     dtype: auto
  #     enforce_eager: true
  #     gpu_memory_utilization: 0.27
  #     max_model_len: 8192

  # reasoning:
  #   runtime: vllm
  #   repository: deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B
  #   parameters:
  #     dtype: auto
  #     enforce_eager: true
  #     gpu_memory_utilization: 0.27
  #     max_model_len: 8192

storage:
  download_dir: ./data/models

huggingface:
  token: ""                      # required for gated models

features:
  tool_calling:
    enabled: true
    parser: hermes               # hermes | mistral | llama3_json

ui:
  enabled: true
  provider: open-webui

gateway:
  enabled: true
  port: 9000
  authentication:
    enabled: true
    api_key: auto                # "auto" = random key generated each deploy

tls:
  enabled: false
```

### GPU memory allocation (multi-model)

When running multiple models on one GPU, `gpu_memory_utilization` values across all deployments should sum to ≤ ~0.90:

```yaml
# Three models on a single A10G (24GB) — leave headroom
deployments:
  chat:
    parameters:
      gpu_memory_utilization: 0.30
  coder:
    parameters:
      gpu_memory_utilization: 0.30
  reasoning:
    parameters:
      gpu_memory_utilization: 0.30
```

### Tool calling

```yaml
features:
  tool_calling:
    enabled: true
    parser: hermes
```

vLLM flags appended when enabled: `--enable-auto-tool-choice --tool-call-parser hermes`

The gateway forwards tool schemas and tool-call responses transparently. Any OpenAI-compatible tool-calling client (LangChain, OpenClaw, Hermes Agent, Open WebUI) works without modification.

---

## API Reference

The gateway exposes a standard OpenAI-compatible API on port `9000`.

All endpoints require `Authorization: Bearer <api-key>` unless authentication is disabled.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Platform info and status |
| `GET` | `/health` | Gateway and deployment health |
| `GET` | `/v1/models` | List available model aliases |
| `POST` | `/v1/chat/completions` | Chat completion (streaming + non-streaming) |

### `GET /health`

```json
{
  "status": "ok",
  "deployments": {
    "chat": "healthy",
    "coder": "healthy",
    "reasoning": "healthy"
  }
}
```

`status` is `"degraded"` when any deployment is unhealthy.

### `POST /v1/chat/completions`

Supported fields:

| Field | Notes |
|-------|-------|
| `model` | Deployment alias or `"auto"` for intelligent routing |
| `messages` | Standard OpenAI messages array |
| `stream` | `true` / `false` |
| `max_tokens` | Clamped to `max_model_len - prompt_tokens` |
| `max_completion_tokens` | Takes precedence over `max_tokens` when both present |
| `tools` | OpenAI tool schemas (forwarded when tool calling is enabled) |
| `tool_choice` | Forwarded transparently |

### Context normalization

The gateway estimates prompt tokens using the deployment's tokenizer and clamps `max_tokens`:

```
effective_max_tokens = min(requested_max_tokens, max_model_len - prompt_tokens)
```

This prevents `context_length_exceeded` errors for clients that don't track token counts.

---

## Agent Integration

### Architecture

```
Agent Clients
  ├─ OpenClaw
  ├─ Hermes Agent
  ├─ LangChain / LangGraph
  └─ Open WebUI
       │
       ↓  POST /v1/chat/completions
  AI Gateway :9000
       │
       ↓
  vLLM Runtime :8000
       │
       ↓
  Self-hosted LLM
```

### OpenClaw

```bash
openclaw config
```

Select `Model → Model/auth provider → More... → vLLM`

| Field | Value |
|-------|-------|
| Base URL | `http://<SERVER_IP>:9000/v1` |
| API Key | Value from `compose.generated.yaml` |
| Model | `chat` |

Use provider **`vllm/chat`** (not legacy custom names).

### Hermes Agent

Add to `~/.hermes/.env`:

```bash
OPENAI_BASE_URL=http://<SERVER_IP>:9000/v1
OPENAI_API_KEY=<gateway-api-key>
```

Recommended Hermes config:

```yaml
provider: openai
model: chat
streaming: true
tool_calling: true
```

### OpenAI SDK / LangChain

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://<SERVER_IP>:9000/v1",
    api_key="<gateway-api-key>",
)

response = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "Hello"}],
)
```

---

## Adding a New Runtime

### 1. Implement the adapter

Create `tools/lib/runtime/<engine>.py`:

```python
from lib.runtime.base import RuntimeAdapter

class MyEngineAdapter(RuntimeAdapter):

    @property
    def image(self) -> str:
        return "my-engine/image:latest"

    def build_command(self, config: dict) -> list[str]:
        return [
            "--model", config["model"]["name"],
            "--port",  str(config["runtime"]["port"]),
        ]
```

### 2. Register it

In `tools/lib/runtime/__init__.py`:

```python
from lib.runtime.my_engine import MyEngineAdapter

_REGISTRY: dict[str, type[RuntimeAdapter]] = {
    "vllm":      VLLMAdapter,
    "my_engine": MyEngineAdapter,
}
```

### 3. Set it in config

```yaml
runtime:
  engine: my_engine
  port: 8000
```

Run `./deploy/scripts/deploy.sh` to deploy with the new runtime.

---

## Project Structure

```
config/
  config.yaml                   ← Project configuration (single source of truth)

deploy/
  compose.yaml                  ← Compose reference template
  compose.generated.yaml        ← Generated compose (do not edit manually)
  caddy/
    Caddyfile                   ← Reverse proxy config
  gateway/
    Dockerfile                  ← Gateway container image
    main.py                     ← ASGI entry point
    requirements.txt
  scripts/
    deploy.sh                   ← Deployment entry point

terraform/
  main.tf                       ← Module composition
  variables.tf
  terraform.tfvars              ← Local overrides (do not commit secrets)
  modules/
    compute/                    ← EC2, spot, EIP, key pair
    identity/                   ← IAM role and instance profile
    network/                    ← VPC, subnet, routing
    security/                   ← Security groups
  scripts/
    bootstrap.sh                ← Instance bootstrap (runs on first boot)
    install_gpu.sh              ← NVIDIA driver installer
    install_gpu_runtime.sh      ← NVIDIA container runtime installer
    auto_gpu_setup.sh           ← Automated GPU setup orchestrator

tools/
  generate.py                   ← Artifact generation CLI
  validate.py                   ← Configuration validation CLI
  requirements.txt
  lib/
    config_loader.py
    compose_generator.py
    validator.py
    gateway/
      app.py                    ← FastAPI application factory
      routes.py                 ← Route handlers
      service.py                ← GatewayService (business logic)
      proxy.py                  ← RuntimeProxy (upstream HTTP client)
      health.py                 ← Deployment health checks
      routing/                  ← RoutingService + keyword classifier
      deployment/               ← GatewayDeploymentRegistry
      middleware/               ← Auth + request ID middleware
      logging/                  ← Structured JSON logging
      transformers/             ← Request/response transformers
    runtime/
      base.py                   ← RuntimeAdapter abstract base class
      vllm.py                   ← vLLM adapter
    models/                     ← Model metadata registry
    openai/                     ← OpenAI schema models and parser
```

---

## Troubleshooting

### Gateway not reachable

```bash
docker ps | grep gateway
curl http://localhost:9000/health
```

Ensure the AWS security group allows inbound TCP 9000.

### `401` authentication errors

The API key is auto-generated on every `generate.py` run. Fetch the current key:

```bash
grep GATEWAY_API_KEY /opt/self-hosted-ai/deploy/compose.generated.yaml
```

### `404 Model not found`

Use a valid deployment alias (`chat`, `coder`, `reasoning`) or `"auto"`. Check available models:

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/v1/models
```

### `400 context_length_exceeded`

The prompt exceeds `max_model_len`. Options:

- Reduce conversation history in the agent
- Increase `max_model_len` in `config.yaml` (requires more VRAM)
- Use a model with a larger native context window

### GPU setup stuck or failed

```bash
sudo systemctl status self-hosted-ai-gpu-setup.service --no-pager
sudo journalctl -u self-hosted-ai-gpu-setup.service -n 200
sudo tail -n 100 /var/log/auto_gpu_setup.log
```

To rerun manually:

```bash
sudo /opt/self-hosted-ai/terraform/scripts/install_gpu.sh
sudo reboot
# after reboot:
sudo /opt/self-hosted-ai/terraform/scripts/install_gpu_runtime.sh
```

Verify GPU access:

```bash
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi
```

### Watch gateway logs

```bash
docker logs gateway -f
# pretty-print JSON
docker logs gateway -f | python3 -m json.tool
# errors only
docker logs gateway -f 2>&1 | grep -i error
```

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full roadmap. Current focus:

- **Milestone 8** — Additional runtimes (SGLang, TensorRT-LLM, llama.cpp, Ollama)
- **Milestone 9** — Observability (Prometheus metrics, Grafana dashboards)
- **Milestone 10** — Platform CLI (`self-hosted-ai deploy/destroy/status/doctor`)

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

Quick summary:
1. Fork the repository and create a feature branch
2. Make your changes and add tests where applicable
3. Run `python3 tools/validate.py` to ensure config validation passes
4. Open a pull request against `main`

For bugs or feature requests, please [open an issue](https://github.com/shreyas-s55/self-hosted-ai/issues).

To report a security vulnerability, see [SECURITY.md](SECURITY.md).

---

## License

[MIT](LICENSE) — see the LICENSE file for details.
