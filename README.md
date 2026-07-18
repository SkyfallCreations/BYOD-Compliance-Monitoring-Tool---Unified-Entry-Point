# BYOD Compliance Monitor

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/badge/code%20style-Ruff-261230)](https://docs.astral.sh/ruff/)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue)](https://mypy-lang.org/)

A Python-based framework for **authorized, transparent, consent-based BYOD compliance assessments** on organization-owned or explicitly enrolled Android devices.

> [!IMPORTANT]
> This repository must only be used on devices you own, administer, or have explicit written authorization to assess. It is not designed for covert surveillance, bypassing device security, hiding collection activity, or collecting private data without informed consent.

## Project status

This repository contains the support files, packaging configuration, installation tooling, policy example, contribution standards, and GitHub automation for the BYOD Compliance Monitor codebase.

The application source is expected to provide a `main.py` entry point and its required `src/` modules. The included validation tool checks the repository structure without pretending missing application modules are present.

## Supported environment

- Python 3.10 or newer
- Windows 10/11, macOS 12+, or a current Linux distribution
- Android Platform Tools (`adb`) when Android connectivity is required
- An Android device enrolled for authorized testing
- USB debugging enabled and approved by the device owner or administrator

## Repository layout

```text
.
├── main.py
├── src/
├── config/
│   └── policy_config.json.example
├── scripts/
│   ├── bootstrap.py
│   ├── validate_repo.py
│   ├── install.sh
│   └── install.ps1
├── tests/
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── .env.example
├── .gitignore
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── Makefile
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── SECURITY.md
└── README.md
```

## Installation

### macOS or Linux

```bash
git clone YOUR_REPOSITORY_URL
cd YOUR_REPOSITORY_FOLDER
chmod +x scripts/install.sh
./scripts/install.sh
```

### Windows PowerShell

```powershell
git clone YOUR_REPOSITORY_URL
Set-Location YOUR_REPOSITORY_FOLDER
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1
```

### Cross-platform Python bootstrap

```bash
python3 scripts/bootstrap.py
```

The bootstrap process:

1. Verifies the Python version.
2. Creates `.venv`.
3. Upgrades `pip`, `setuptools`, and `wheel`.
4. Installs runtime and development dependencies.
5. Creates local runtime directories.
6. Copies `config/policy_config.json.example` to `config/policy_config.json` when needed.
7. Runs repository validation.

## Activate the virtual environment

### macOS or Linux

```bash
source .venv/bin/activate
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

## Verify the repository

```bash
python scripts/validate_repo.py
```

Strict validation, including application source expectations:

```bash
python scripts/validate_repo.py --strict
```

Development checks:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy scripts
python -m pytest
```

Or run:

```bash
make check
```

## Configuration

Copy the example policy file before first use:

```bash
cp config/policy_config.json.example config/policy_config.json
```

Windows:

```powershell
Copy-Item config\policy_config.json.example config\policy_config.json
```

The example policy intentionally contains safe sample values. Review every setting before using the application in an organization.

Never commit:

- Real device identifiers
- Employee or customer data
- Extracted messages, contacts, call records, or location records
- Authentication material
- Private keys
- Production policy files containing sensitive organizational details

## Authorized usage model

A compliant deployment should include:

- Written authorization
- Informed user notice and consent where required
- Data minimization
- Least-privilege access
- Defined retention limits
- Audit logging
- Encryption at rest
- A documented deletion process
- Legal and human-resources review when applicable

## Running the application

The exact command-line options depend on the application source currently in `main.py`.

Start by checking its built-in help:

```bash
python main.py --help
```

Do not run collection operations until the device owner or authorized administrator has approved the scope.

## Security

Report security issues privately using the process in [SECURITY.md](SECURITY.md). Do not include sensitive device data in public issues.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

Licensed under the MIT License. See [LICENSE](LICENSE).

## Disclaimer

This project is provided for legitimate device administration, internal compliance validation, security testing, and development on authorized systems. Users are responsible for complying with all applicable laws, employment policies, contracts, privacy requirements, and consent obligations.
