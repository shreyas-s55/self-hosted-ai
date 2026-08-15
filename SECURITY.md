# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.1.x   | Yes       |
| < 0.1.0 | No        |

## Reporting a Vulnerability

Please do not report security vulnerabilities in public GitHub issues,
discussions, or pull requests.

Use GitHub Private Vulnerability Reporting for this repository when it is
available. If private reporting is not enabled in the hosting repository,
contact the maintainers through a private channel provided by the repository
owner and include:

- A clear description of the issue and the affected component
- Reproduction steps or a proof of concept
- The potential impact
- Any suggested mitigation, if known

Examples of security-sensitive issues include:

- Authentication or authorization bypasses in the gateway
- Exposure of API keys, Hugging Face tokens, or deployment secrets
- SSRF, open proxy behavior, or unsafe request forwarding
- Terraform or bootstrap paths that unintentionally expose infrastructure

## Response Process

The maintainers will make a best effort to:

- Acknowledge receipt within 5 business days
- Assess severity and scope
- Work on a fix or mitigation
- Coordinate a disclosure timeline with the reporter
- Credit the reporter in release notes unless they prefer to remain anonymous

## Disclosure Expectations

Please give the maintainers a reasonable amount of time to investigate and
remediate the issue before public disclosure. We will share remediation details
in the changelog and release notes once a fix is available.