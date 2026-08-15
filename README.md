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

## Agent Integration

The platform provides a production-grade OpenAI-compatible API that autonomous
agents can consume without modification.

### Architecture

```
Agent Clients
  ├─ OpenClaw
  ├─ Hermes Agent
  └─ Open WebUI
       │
       ↓
OpenAI-compatible API
       │
       ↓
AI Gateway :9000
       │
       ↓
vLLM Runtime
       │
       ↓
Self-hosted LLM
```

Agents never communicate directly with vLLM. The gateway provides:

- **Authentication** — Bearer token validation
- **OpenAI API compatibility** — `/v1/chat/completions` endpoint
- **Routing** — Model alias resolution to physical deployments
- **Context normalization** — Prompt-aware `max_tokens` clamping
- **Runtime abstraction** — Clients remain agnostic to the inference engine

### Supported Fields

The gateway transparently supports both OpenAI token budget fields:

| Field | Support | Notes |
|-------|---------|-------|
| `max_tokens` | ✅ Full | Legacy OpenAI field |
| `max_completion_tokens` | ✅ Full | Newer OpenAI field |

When both are present, `max_completion_tokens` takes precedence. The gateway
always normalizes to `max_tokens` before forwarding to vLLM.

## Goals

- Single EC2 deployment
- Terraform automation
- Docker Compose with generated configuration
- OpenAI-compatible API
- Open WebUI
- Autonomous agent support
- OpenClaw compatibility
- Hermes Agent compatibility
- OpenAI-compatible agent ecosystem
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

On a fresh instance, this now bootstraps the machine and brings up the default
single-model platform automatically. For GPU instances, the instance will
install the NVIDIA driver, reboot once, install the NVIDIA container runtime,
verify GPU access, and then deploy the stack.

### 2. Install GPU Drivers

For GPU instances, bootstrap now installs the NVIDIA driver automatically,
reboots once, installs the NVIDIA container runtime, verifies `nvidia-smi`,
and then runs the default single-model deployment.

You can watch progress after SSH:

```bash
sudo tail -f /var/log/auto_gpu_setup.log
```

You can also inspect the automation service directly:

```bash
sudo systemctl status self-hosted-ai-gpu-setup.service --no-pager
sudo journalctl -u self-hosted-ai-gpu-setup.service -n 100 -f
```

If you need to rerun the steps manually, the underlying commands are still:

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

The default deployment is now automated during bootstrap.

After the automation completes, the default stack should already be running:

```bash
cd /opt/self-hosted-ai/deploy
sudo docker compose -f compose.generated.yaml --env-file .env ps
```

**Single model** (default — one model, one GPU):

```bash
sudo /opt/self-hosted-ai/deploy/scripts/deploy.sh
```

If you want to switch later, SSH to the instance and run one of the alternate
modes.

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

### 5. OpenClaw Agent Setup

[OpenClaw](https://openclaw.ai) is an autonomous AI agent that operates through
an OpenAI-compatible API.

**Installation:**

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Configuration:**

```bash
openclaw config
```

Select:

```
Model
  → Model/auth provider
    → More...
      → vLLM
```

**Configuration values:**

| Field | Value |
|-------|-------|
| Base URL | `http://<SERVER_IP>:9000/v1` |
| API Key | `<Gateway API key from compose.generated.yaml>` |
| Model | `chat` |

**Important:** Use the model provider **`vllm/chat`** in OpenClaw's configuration,
not legacy custom provider names. This ensures compatibility with the gateway's
routing layer.

### 6. Hermes Agent Setup

[Hermes Agent](https://github.com/coleam00/hermes-agent) connects using the
standard OpenAI-compatible endpoint.

**Configuration:**

Add to `~/.hermes/.env`:

```bash
OPENAI_BASE_URL=http://<SERVER_IP>:9000/v1
OPENAI_API_KEY=<Gateway API key>
```

**Endpoint compatibility:**

| Endpoint | Support | Notes |
|----------|---------|-------|
| `POST /v1/chat/completions` | ✅ Full | Streaming and non-streaming |
| `GET /v1/models` | ✅ Full | Lists available deployment aliases |
| `POST /v1/embeddings` | ❌ Not implemented | Future enhancement |

**Recommended Hermes configuration:**

```yaml
provider: openai
model: chat
streaming: true
tool_calling: true
```

The gateway also normalizes oversized client `max_tokens` values before
forwarding requests. For each routed deployment, it loads the deployment's
tokenizer, estimates prompt tokens from the forwarded chat payload, and clamps
the requested completion budget to the remaining space inside
`deployments.<alias>.parameters.max_model_len`.

## Agent Troubleshooting

### Health Check

Verify the gateway is reachable and healthy:

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/health
```

Expected response:

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

### List Available Models

Query the deployed model aliases:

```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:9000/v1/models
```

### Gateway Logs

Monitor gateway requests in real time:

```bash
docker logs gateway -f
```

Filter for errors only:

```bash
docker logs gateway -f 2>&1 | grep -i error
```

### Common Issues

**Wrong model selected**

Symptom: `404 Model not found`

Solution: Use `chat`, `coder`, or `reasoning` as the model name. For OpenClaw,
select the `vllm/chat` provider.

---

**Authentication failure**

Symptom: `401 Missing API key` or `401 Invalid API key`

Solution: The gateway API key is auto-generated on each `generate.py` run. After
regenerating deployment artifacts, update the agent configuration:

```bash
grep GATEWAY_API_KEY deploy/compose.generated.yaml
```

---

**Context length errors**

Symptom: `400 context_length_exceeded`

Solution: The prompt alone exceeds the deployment's `max_model_len`. Either:

- Reduce conversation history in the agent
- Decrease `max_model_len` in `config.yaml` (increases available prompt space)
- Deploy a model with a larger native context window

---

**Connection refused**

Symptom: Agent cannot reach `http://<SERVER_IP>:9000`

Solution: Verify the gateway container is running and port 9000 is accessible:

```bash
docker ps | grep gateway
curl http://localhost:9000/health
```

If running remotely, ensure AWS security group allows inbound TCP port 9000.

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
this translates to:

```bash
--enable-auto-tool-choice --tool-call-parser hermes
```

The gateway transparently forwards tool schemas and tool-call responses between
agents and vLLM. Agents that support OpenAI-compatible tool calling (OpenClaw,
Hermes Agent, LangChain, Open WebUI) work without modification.

Set `enabled: false` to disable tool calling without removing the section.

### Gateway Token Ceiling

The gateway computes a prompt-aware completion budget for any request that
includes `max_tokens`.

Example:

```yaml
deployments:
  chat:
    runtime: vllm
    repository: Qwen/Qwen2.5-1.5B-Instruct
    default: true
    parameters:
      max_model_len: 8192
```

With this deployment, a client request such as `max_tokens: 65536` is rewritten
to the smaller of:

- the client-requested `max_tokens`
- `max_model_len - prompt_tokens`

Prompt tokens are estimated with the routed model's tokenizer against the same
chat payload the gateway forwards upstream, including tool schemas when they are
present. This keeps the OpenAI-compatible endpoint stable for Hermes, Open WebUI,
LangChain, the OpenAI SDK, and other clients while preserving per-deployment
routing.

### Recommended Agent Model

For production agent workloads on `g6.xlarge` (A10G 24GB GPU), the following
profile has been validated with OpenClaw and Hermes Agent:

```yaml
deployments:
  chat:
    runtime: vllm
    repository: Qwen/Qwen2.5-7B-Instruct
    default: true
    parameters:
      dtype: auto
      enforce_eager: true
      gpu_memory_utilization: 0.95
      max_model_len: 32768
```

**Optimized for:**

- A10G 24GB VRAM
- Multi-turn agent conversations
- Tool calling with Hermes parser
- Long context windows (up to 32K tokens)
- Stable vLLM operation under continuous load

**Alternative for memory-constrained environments:**

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
```

This smaller model fits three concurrent deployments on a single `g6.xlarge`
in multi-mode.

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

