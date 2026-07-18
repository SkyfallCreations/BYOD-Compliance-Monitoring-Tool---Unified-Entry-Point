# Security Policy

## Supported versions

Security fixes are applied to the latest maintained release.

| Version | Supported |
|---|---|
| 1.x | Yes |
| Earlier | No |

## Reporting a vulnerability

Do not disclose sensitive vulnerabilities, device data, credentials, or personal information in a public issue.

Use GitHub private vulnerability reporting when enabled for the repository. Include:

- Affected version or commit
- Impact
- Reproduction steps using synthetic data
- Suggested mitigation, when known

Do not include real messages, contacts, call records, locations, device identifiers, access tokens, or production configuration.

## Scope restrictions

The project must not be used to:

- Access devices without authorization
- Hide monitoring from a device owner
- Bypass authentication or platform security
- Collect more data than an approved assessment requires
- Maintain unauthorized persistence
- Conceal evidence of collection
- Exfiltrate data

## Handling sensitive data

Use synthetic test fixtures whenever possible. Production data must be encrypted, access-controlled, minimized, retained only as required, and destroyed through an approved process.
