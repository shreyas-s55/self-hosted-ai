# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-08-15

### Added

- Initial open source release of Self-Hosted AI
- Terraform-based AWS infrastructure provisioning for VPC, IAM, security
  groups, EC2, bootstrap automation, and GPU runtime setup
- Runtime abstraction layer with a vLLM adapter and runtime registry
- Configuration-driven deployment tooling for validation, environment
  generation, and Docker Compose rendering
- Integrated services for the custom FastAPI gateway, Open WebUI, and Caddy
- OpenAI-compatible gateway endpoints, runtime proxying, and health checks
- Deployment-generated API key authentication and automatic UI wiring
- Structured JSON logging, request IDs, startup diagnostics, and system info
- Intelligent `model="auto"` routing for chat, coding, and reasoning prompts
- Multi-deployment support for shared-GPU and dedicated multi-GPU profiles

### Notes

- This release captures completed roadmap milestones 1 through 7.
- Future work will focus on runtime expansion, observability, and a platform
  CLI.