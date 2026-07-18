# BYOD Compliance Monitoring Tool

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Android-brightgreen)](https://www.android.com/)

Enterprise-grade BYOD (Bring Your Own Device) compliance monitoring solution for Android devices. Extracts, analyzes, and reports on SMS/MMS messages, contacts, call logs, and device locations to ensure corporate policy compliance.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Modules](#modules)
- [Output & Reports](#output--reports)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Features

### Core Capabilities
- **SMS/MMS Extraction**: Complete message history extraction with thread reconstruction
- **Contact Extraction**: Full contacts database parsing with compliance filtering
- **Call Log Monitoring**: Detailed call history with duration and frequency analysis
- **Location Tracking**: GPS and network location history with geofencing support
- **Real-Time Monitoring**: Continuous SMS monitoring with instant violation alerts
- **Compliance Engine**: Policy-based violation detection and reporting
- **Stealth Operation**: Covert monitoring mode for sensitive investigations
- **Automated Cleanup**: Complete artifact removal for operational security

### Compliance Features
- **Domain Filtering**: Identify contacts from forbidden email domains
- **Organization Detection**: Flag contacts from competitor organizations
- **Keyword Scanning**: Real-time message scanning for sensitive keywords
- **Personal Contact Limits**: BYOD personal contact policy enforcement
- **Location Geofencing**: Detect unauthorized device locations
- **Audit Trail**: Complete logging of all monitoring activities

### Reporting
- **Multiple Formats**: HTML, JSON, and text report generation
- **Comprehensive Analytics**: Contact patterns, communication frequency, risk scoring
- **Violation Summaries**: Detailed policy violation reports with evidence
- **Export Capabilities**: Structured data export for SIEM integration

---

## 🏗 Architecture

byod-compliance-monitor/ 
├── main.py                          # Unified entry point 
├── config/ 
│   └── policy_config.json           # Compliance policy configuration 
├── src/ 
│   ├── adb_interface.py             # Android Debug Bridge interface 
│   ├── contact_extractor.py         # Contacts database extraction 
│   ├── sms_extractor.py             # SMS/MMS extraction & parsing 
│   ├── sms_monitor.py               # Real-time SMS monitoring 
│   ├── call_log_extractor.py        # Call log extraction 
│   ├── location_tracker.py          # GPS/location history 
│   ├── message_analyzer.py          # Message content analysis 
│   ├── compliance_engine.py         # Policy enforcement & violation detection 
│   ├── stealth_manager.py           # Stealth operation management 
│   ├── report_generator.py          # Multi-format report generation 
│   ├── db_handler.py                # SQLite compliance database 
│   └── cleanup_manager.py           # Artifact removal & data wiping 
├── logs/ 
│   └── byod_monitor.log             # Operation logs 
├── output/ 
│   └── compliance_reports/          # Generated compliance reports 
├── temp_data/                       # Temporary extraction storage 
├── requirements.txt                 # Python dependencies 
└── README.md                        # This file


### Data Flow

Device → ADB Interface → Extractors → Analyzer → Compliance Engine → Reporter 
↓                    ↓ 
temp_data/          Compliance DB


---

## 📦 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 11+, Linux (Ubuntu 20.04+, Debian 11+)
- **RAM**: Minimum 4GB, recommended 8GB
- **Storage**: 500MB free space minimum

### Android Device Requirements
- **Android Version**: 8.0 (Oreo) or higher
- **USB Debugging**: Enabled in Developer Options
- **Root Access**: Required for full extraction (contacts database, call logs)
- **Permissions**: SMS, Contacts, Location permissions granted

### Development Tools
- **Android SDK Platform Tools**: ADB and fastboot
- **USB Driver**: Manufacturer-specific drivers (Windows only)

---

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/byod-compliance-monitor.git
cd byod-compliance-monitor

2. Install Python Dependencies

pip install -r requirements.txt

3. Configure Android Device

4. Enable Developer Options: Settings → About Phone → Tap "Build Number" 7 times
5. Enable USB Debugging: Settings → Developer Options → USB Debugging
6. Connect Device: USB cable to computer
7. Authorize Connection: Accept RSA key fingerprint on device

8. Verify Setup

# Check device connectivity
adb devices

# Should show your device as "device" (not "unauthorized")

---
⚙️ Configuration

Policy Configuration (config/policy_config.json)

Create your compliance policy configuration:

{
  "adb_timeout": 30,
  "sms_policy": {
    "monitor_inbound": true,
    "monitor_outbound": true,
    "forbidden_keywords": [
      "classified",
      "confidential",
      "proprietary",
      "internal only"
    ],
    "max_message_length": 1000,
    "log_all_messages": true,
    "alert_on_forbidden_keywords": true
  },
  "contact_policy": {
    "max_personal_contacts": 50,
    "forbidden_domains": [
      "competitor.com",
      "competitor.org"
    ],
    "forbidden_organizations": [
      "Competitor Corp",
      "Rival Inc"
    ],
    "require_organization_info": true
  },
  "location_policy": {
    "track_during_business_hours": true,
    "business_hours": {
      "start": "08:00",
      "end": "18:00",
      "timezone": "America/New_York",
      "days": [1, 2, 3, 4, 5]
    },
    "store_history_days": 30,
    "location_sample_interval_seconds": 300,
    "geofence_locations": [
      {
        "name": "Main Office",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius_meters": 500
      }
    ],
    "alert_on_geofence_violation": true
  },
  "call_policy": {
    "monitor_calls": true,
    "log_call_duration": true,
    "alert_on_long_calls": true,
    "max_call_duration_minutes": 120
  },
  "stealth": {
    "enabled": false,
    "hide_notifications": true,
    "clear_logs": true,
    "use_encryption": true
  },
  "reporting": {
    "output_format": "json",
    "generate_html_report": true,
    "generate_text_report": false,
    "include_raw_data": true,
    "compression_level": 6
  }
}

---
💻 Usage

Basic Commands

# Complete extraction pipeline
python main.py --full

# SMS extraction only
python main.py --sms-only

# Contacts extraction only
python main.py --contacts-only

# Real-time SMS monitoring
python main.py --monitor --duration 60

# Target specific device
python main.py --device 123ABC123 --full

# Stealth mode extraction
python main.py --stealth --full

# Generate specific report format
python main.py --full --report-format html

# Cleanup all artifacts
python main.py --cleanup

# Verbose logging for debugging
python main.py --full --verbose

Advanced Usage Examples

# Full compliance audit with stealth mode and HTML report
python main.py --stealth --full --report-format html --output ./audit_reports/

# Monitor for 2 hours targeting specific device with verbose logging
python main.py --monitor --duration 120 --device emulator-5554 --verbose

# Quick check during incident response
python main.py --sms-only --contacts-only --output ./incident_response/

# Scheduled compliance check (add to crontab)
0 6 * * 1 cd /path/to/tool && python main.py --full --report-format html

Real-Time Monitoring

The real-time monitoring mode:

· Continuously watches for new SMS messages 
· Analyzes content in real-time for policy violations 
· Alerts immediately on detection of forbidden content 
· Logs all violations to compliance database 
· Can run indefinitely or for a specified duration 
· Supports graceful shutdown with Ctrl+C
---
🧩 Modules

Contact Extractor (contact_extractor.py)

Extracts and parses the complete Android contacts database (contacts2.db):

· Supported Fields: Names, phones, emails, organizations, photos 
· Account Types: Google, Exchange, Samsung, custom accounts 
· Compliance Features: Domain filtering, organization detection 
· Output: Structured Contact objects with all metadata

SMS Extractor (sms_extractor.py)

Extracts complete SMS/MMS history from Android SMS database:

· Database: mmssms.db from the telephony provider 
· Threading: Reconstructs conversation threads 
· MMS Support: Extracts multimedia message content 
· Export: JSON export with full metadata

SMS Monitor (sms_monitor.py)

Real-time SMS monitoring with minimal resource footprint:

· Detection Method: Content observer or polling 
· Callback System: Instant notification of new messages 
· Performance: Optimized for continuous operation

Location Tracker (location_tracker.py)

Extracts and monitors device location history:

· Sources: GPS, Network, WiFi, Cell Tower 
· Geofencing: Configurable location boundaries 
· History: Configurable retention period

Compliance Engine (compliance_engine.py)

Enforces all policy rules and generates violations:

· SMS Analysis: Content scanning, keyword detection 
· Contact Verification: Domain, organization checks 
· Location Validation: Geofence violation detection 
· Risk Scoring: Calculates compliance risk scores
---
📊 Output & Reports

Report Formats

HTML Report

· Interactive dashboard with charts and tables 
· Violation summaries with evidence 
· Communication pattern visualization 
· Risk score heatmaps 
· Export to PDF capability

JSON Report

· Structured data for SIEM integration 
· Complete raw data preservation 
· Timestamps and metadata 
· Violation evidence chains

Text Report

· Console-friendly format 
· Summary statistics 
· Violation listings 
· Quick scan overview

Output Directory Structure

output/
├── compliance_report_20240115_143022.html
├── compliance_report_20240115_143022.json
├── contacts_export.json
├── sms_export.json
├── call_logs_export.json
└── locations_export.json

---
🔒 Security Considerations

Important Security Notes

⚠️ This tool is designed for authorized enterprise monitoring only.

1. Legal Compliance 
2. · Ensure compliance with local laws and regulations 
3. · Obtain proper consent from device owners 
4. · Document monitoring policies and procedures 
5. · Consult legal counsel before deployment
6. Data Protection 
7. · All extracted data is stored locally 
8. · No cloud transmission without explicit configuration 
9. · Implement proper access controls on output directories 
10. · Encrypt sensitive report files when at rest
11. Operational Security 
12. · Use stealth mode for sensitive investigations 
13. · Implement proper access logging 
14. · Regular cleanup of temporary files 
15. · Secure the logs directory from unauthorized access
16. Best Practices 
17. · Run in isolated, secured environments 
18. · Use dedicated service accounts 
19. · Implement audit trails for tool usage 
20. · Regular security reviews and updates

Data Classification

Data Type Sensitivity Storage Encryption 
SMS Content High Local DB Optional 
Contacts High Local DB Optional 
Call Logs Medium Local DB Optional 
Location Data High Local DB Optional 
Reports High Output Dir Recommended 
Logs Medium Logs Dir Optional
---
🔍 Troubleshooting

Common Issues

Device Not Found

# Verify ADB connection
adb devices
# Kill and restart ADB server
adb kill-server && adb start-server
# Check USB connection and authorization

Permission Denied Errors

# Ensure USB debugging is enabled
# Re-authorize device connection
# Check for root access if required
adb root

Database Access Issues

# Verify database paths
adb shell ls -la /data/data/com.android.providers.contacts/databases/
# Check permissions
adb shell whoami

Module Import Errors

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
# Verify Python path
python -c "import sys; print(sys.path)"

Logging

Enable verbose logging for detailed debugging:

python main.py --full --verbose

Logs are stored in logs/byod_monitor.log with timestamps and severity levels.
---
📝 Dependencies

Create a requirements.txt file:

# requirements.txt
# Core dependencies

# No external dependencies required for core functionality
# All modules use Python standard library

# Optional dependencies for enhanced features
# pandas>=2.0.0  # For advanced data analysis
# jinja2>=3.1.2  # For HTML report templates
# cryptography>=41.0.0  # For stealth mode encryption

Python Standard Library Used

· sqlite3 - Database operations 
· json - Configuration and export 
· pathlib - File system operations 
· argparse - Command-line interface 
· logging - Operation logging 
· datetime - Timestamp handling 
· subprocess - ADB command execution
---
🤝 Contributing

Development Setup

# Fork and clone repository
git clone https://github.com/yourusername/byod-compliance-monitor.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

Additional Files You Should Add

Based on the project structure, consider adding these files:

1. .gitignore

# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
build/
*.egg

# Virtual Environment
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project Specific
temp_data/
output/
logs/
*.db
*.log
config/policy_config.json

# OS
.DS_Store
Thumbs.db

# Sensitive
credentials.json
*.pem
*.key

2. setup.py for package distribution

from setuptools import setup, find_packages

setup(
    name="byod-compliance-monitor",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    python_requires='>=3.8',
)

3. LICENSE file (MIT recommended)
4. CONTRIBUTING.md for contribution guidelines
5. CHANGELOG.md for version history
---
📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
---
⚠️ Disclaimer

This tool is intended for legitimate enterprise security monitoring and compliance purposes only. Users are responsible for:

· Obtaining proper authorization before monitoring any device 
· Complying with all applicable laws and regulations 
· Maintaining appropriate data protection measures 
· Documenting and communicating monitoring policies 
· Obtaining legal counsel for deployment in regulated environments

The authors assume no liability for unauthorized or illegal use of this software.
---
📞 Support

For support, bug reports, or feature requests:

· Open an issue on GitHub 
· Contact your organization's security team 
· Review the troubleshooting guide above
---
🙏 Acknowledgments

Built with dedication and attention to detail. Special thanks to:

· The Android Open Source Project 
· The Python community 
· Enterprise security professionals worldwide
---
Version: 1.0.0 
Last Updated: January 2024 
Status: Production Ready 
Python: 3.8+ 
Platform: Android 8.0+
---
"Security is not a product, but a process." - Bruce Schneier


This README.md covers everything from your codebase and our discussions. You should also add these files to complete your repository:

1. **`.gitignore`** (provided above)
2. **`requirements.txt`** (provided above)
3. **`LICENSE`** (MIT recommended)
4. **`config/policy_config.json.example`** (copy your config but remove sensitive data)
5. **`.env.example`** if you use environment variables

The README is production-ready with comprehensive documentation covering all aspects of your tool.
