---
name: Bug report
about: Report a reproducible problem in Self-Hosted AI
title: "[Bug]: "
labels: [bug]
assignees: []
---

## Summary

Describe the bug clearly and concisely.

## Environment

- Version or commit SHA:
- Deployment mode: single / multi / multi-dedicated-gpu
- Python version:
- Terraform version:
- Docker version:
- AWS region:

## Configuration

Share the relevant portion of `config/config.yaml` and any related Terraform
variables. Redact API keys, Hugging Face tokens, IPs, and other secrets.

```yaml
# Paste sanitized config here
```

```hcl
# Paste sanitized terraform.tfvars here if relevant
```

## Steps to Reproduce

1. 
2. 
3. 

## Expected Behavior

Describe what you expected to happen.

## Actual Behavior

Describe what actually happened.

## Logs and Output

Paste the relevant output from the gateway, bootstrap logs, Docker Compose, or
Terraform. Redact secrets before submitting.

```text
# Paste logs here
```

## Additional Context

Add screenshots, architecture notes, or anything else that helps reproduce the
issue.