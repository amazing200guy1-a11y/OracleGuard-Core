# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | Yes       |

## Reporting a Vulnerability

Do NOT open a public GitHub issue for security reports.

Contact: security@mehd.ai — Subject: `[SECURITY] OracleGuard-Core`

Response expected within 48 hours.

## Design Notes

- All feed credentials passed via environment variables only.
- Manipulation detection threshold is deterministic and cannot be soft-overridden at runtime.
- Fail-closed: any parse error or timeout raises immediately — no silent degradation.