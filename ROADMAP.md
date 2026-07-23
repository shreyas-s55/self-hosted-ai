# self-hosted-ai Roadmap

## Vision

Build a lightweight, production-quality, self-hosted AI inference platform that can be deployed on demand with Terraform, run for a few hours or days, and destroyed without operational overhead.

The platform should expose an OpenAI-compatible API while remaining runtime-agnostic, configuration-driven, and easy to extend.

---

# Guiding Principles

- Infrastructure as Code (Terraform)
- Configuration-driven deployment
- Runtime abstraction
- Stateless services
- Ephemeral infrastructure
- OpenAI API compatibility
- Low operational overhead
- Modular architecture
- Security by default

---

# Completed

## Milestone 1 — Infrastructure

- Terraform project structure
- VPC
- IAM
- Security Groups
- EC2 provisioning
- Bootstrap scripts
- Docker installation
- NVIDIA runtime support

Status: ✅

---

## Milestone 2 — Runtime Platform

- Runtime abstraction
- vLLM adapter
- Runtime registry
- Configuration-driven runtime selection

Status: ✅

---

## Milestone 3 — Deployment Platform

- Service registry
- Compose generator
- Environment generation
- Validation
- Open WebUI integration
- Caddy integration

Status: ✅

---

## Milestone 4 — AI Gateway

- FastAPI gateway
- OpenAI-compatible endpoints
- Runtime proxy
- Health endpoints
- Gateway service

Status: ✅

---

## Milestone 5 — Authentication

- Deployment-generated API key
- Gateway authentication middleware
- Automatic Open WebUI configuration
- Stateless authentication
- Ephemeral deployment model

Status: ✅

---

## Milestone 6 — Gateway Foundation

- Request IDs
- Structured JSON logging
- Startup banner
- System information endpoint
- Basic metrics

Status: ✅

---

## Milestone 7 — Intelligent Routing

- `model="auto"` request routing
- Rule-based keyword classifier (coding / reasoning / chat)
- Deployment-driven gateway forwarding
- Multi-deployment configuration format
- Per-deployment health reporting
- Single-GPU multi-model deployment (enforce_eager + sequential startup)
- Multi-GPU deployment with per-container GPU pinning (`--pin-gpus`)

Status: ✅

---

# Current Milestone

## Milestone 8 — Runtime Expansion

- SGLang
- TensorRT-LLM
- llama.cpp
- Ollama

---

## Milestone 9 — Observability

- Metrics endpoint
- Prometheus integration
- Grafana dashboards
- Health aggregation

---

## Milestone 10 — Platform CLI

Commands such as:

self-hosted-ai deploy

self-hosted-ai destroy

self-hosted-ai doctor

self-hosted-ai status

---

## Future

- Agent integration
- OpenHands
- OpenClaw
- LangGraph
- Workflow execution
- Plugin system