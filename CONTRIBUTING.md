# Contributing

Thank you for helping improve the BYOD Compliance Monitor.

## Ground rules

Contributions must support authorized, transparent, consent-based device administration. Pull requests that add covert surveillance, credential bypass, evasion, hidden persistence, unauthorized data collection, or anti-forensic behavior will not be accepted.

## Development setup

```bash
python3 scripts/bootstrap.py
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python scripts\bootstrap.py
.venv\Scripts\Activate.ps1
```

## Before submitting

Run:

```bash
python scripts/validate_repo.py --strict
python -m ruff check .
python -m ruff format --check .
python -m mypy scripts
python -m pytest
```

## Pull requests

A pull request should:

1. Explain the problem.
2. Describe the implemented change.
3. Identify security and privacy impact.
4. Include or update tests.
5. Update documentation when behavior changes.
6. Avoid unrelated refactoring.

## Commit messages

Use a direct imperative style:

```text
Add repository validation for configuration files
Fix Windows virtual-environment activation instructions
Document authorized device enrollment requirements
```

## Reporting security defects

Do not open a public issue for a security vulnerability. Follow [SECURITY.md](SECURITY.md).
