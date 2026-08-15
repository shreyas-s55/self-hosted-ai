# Contributing to Self-Hosted AI

Thank you for your interest in contributing! This document explains how to set up a development environment, submit changes, and follow project conventions.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Project Conventions](#project-conventions)
- [Testing](#testing)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

---

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

---

## Ways to Contribute

- **Bug reports** — File an issue with reproduction steps
- **Feature requests** — Open an issue describing the use case
- **Documentation** — Fix typos, improve examples, expand guides
- **Bug fixes** — Reference the issue in your PR
- **New runtimes** — Implement a `RuntimeAdapter` for a new inference engine
- **New features** — Discuss in an issue first before large changes

---

## Getting Started

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (for integration testing)
- Terraform ≥ 1.9 (for infrastructure changes)

### Set up the development environment

```bash
git clone https://github.com/your-org/self-hosted-ai.git
cd self-hosted-ai

# Install tools dependencies
pip install -r tools/requirements.txt

# Install gateway dependencies
pip install -r deploy/gateway/requirements.txt

# Install linting tools
pip install ruff
```

### Validate config tooling works

```bash
python3 tools/validate.py
python3 tools/generate.py
```

Both should complete without errors against the default `config/config.yaml`.

---

## Development Workflow

### Branching

- `main` — stable, protected, always deployable
- Feature branches — `feat/<short-description>`
- Bug fix branches — `fix/<short-description>`
- Documentation branches — `docs/<short-description>`

```bash
git checkout -b feat/add-sglang-runtime
```

### Directory layout

| Area | Path | Notes |
|------|------|-------|
| Gateway source | `tools/lib/gateway/` | Deployed into `deploy/gateway/` via Dockerfile |
| Runtime adapters | `tools/lib/runtime/` | One file per engine |
| Config tooling | `tools/` | `validate.py`, `generate.py`, and `lib/` |
| Infrastructure | `terraform/` | Modules under `modules/` |
| Compose reference | `deploy/compose.yaml` | Hand-edited template |
| Generated artifacts | `deploy/compose.generated.yaml`, `deploy/.env` | Never edit manually |

### Gateway code lives in `tools/lib/`

The gateway source (`tools/lib/gateway/`) is shared between the tooling and the container. The Dockerfile copies `tools/lib/` directly into the image:

```dockerfile
COPY tools/lib/ ./lib/
```

Changes to `tools/lib/gateway/` are picked up on the next `deploy.sh` run.

---

## Project Conventions

### Python

- Style: [PEP 8](https://peps.python.org/pep-0008/), enforced with `ruff`
- Type hints: required for all public functions and methods
- Docstrings: module-level and public classes/functions; use one-line imperative style
- No unused imports

Run the linter:

```bash
ruff check tools/
```

Auto-fix:

```bash
ruff check --fix tools/
```

### Terraform

- Format: `terraform fmt -recursive`
- Every variable must have a `description`
- Every module must have an `outputs.tf` (even if empty)
- No hard-coded AMI IDs — use data sources

### Shell scripts

- All scripts must start with `set -euo pipefail`
- Quote all variable expansions: `"$var"` not `$var`
- No silent failures

### Configuration

- `config/config.yaml` is the single source of truth
- New configuration keys must be handled in `tools/lib/validator.py` and `tools/lib/compose_generator.py`
- Add a commented example of any new optional key to the default `config.yaml`

---

## Testing

### Config validation

```bash
python3 tools/validate.py
```

### Config generation

```bash
python3 tools/generate.py
# Verify output
cat deploy/compose.generated.yaml
cat deploy/.env
```

### Multi-model generation

```bash
python3 tools/generate.py --profile multi
python3 tools/generate.py --profile multi --pin-gpus
```

### Gateway unit tests

The gateway has unit tests in `tools/lib/gateway/`:

```bash
# From the project root
python3 -m pytest tools/ -v
```

### Terraform validation

```bash
cd terraform
terraform init -backend=false
terraform validate
terraform fmt -check -recursive
```

---

## Submitting a Pull Request

1. **Fork** the repository and create a branch off `main`
2. **Make your changes** — keep commits focused and atomic
3. **Run validation** — config tooling and linter must pass
4. **Update documentation** — update `README.md`, `ROADMAP.md`, or inline docstrings as needed
5. **Open the PR** — fill in the pull request template
6. **Respond to review** — address feedback; force-push to the same branch

### PR checklist

- [ ] `ruff check tools/` passes
- [ ] `python3 tools/validate.py` passes
- [ ] `python3 tools/generate.py` produces valid output
- [ ] `terraform validate` passes (for infrastructure changes)
- [ ] Existing tests pass
- [ ] New behavior is covered by tests or manual verification steps are documented
- [ ] `README.md` updated if user-facing behavior changed

### Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add SGLang runtime adapter
fix: clamp max_tokens before forwarding to vllm
docs: add multi-GPU deployment example
chore: update vllm image to v0.9.0
refactor: extract token estimation into TokenBudget helper
```

---

## Reporting Bugs

Open a [bug report issue](https://github.com/your-org/self-hosted-ai/issues/new?template=bug_report.md).

Include:
- Self-Hosted AI version or commit SHA
- OS and Python version
- Relevant section of `config/config.yaml` (redact tokens)
- Full error output or log snippet
- Steps to reproduce

---

## Requesting Features

Open a [feature request issue](https://github.com/your-org/self-hosted-ai/issues/new?template=feature_request.md).

For large features, discuss the design in the issue before opening a PR. This saves effort if the direction needs adjustment.
