#!/bin/bash
# BYOD Compliance Monitor - Linux/macOS Installation Script

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}BYOD Compliance Monitor - Installer${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Check Python installation
echo -e "${GREEN}[1/4] Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo -e "  Found: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1)
    echo -e "  Found: $PYTHON_VERSION"
else
    echo -e "${RED}  [ERROR] Python not found! Please install Python 3.8+${NC}"
    echo -e "${YELLOW}  Ubuntu/Debian: sudo apt-get install python3 python3-pip${NC}"
    echo -e "${YELLOW}  macOS: brew install python3${NC}"
    exit 1
fi

# Check Python version
PYTHON_VER=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if (( $(echo "$PYTHON_VER < 3.8" | bc -l) )); then
    echo -e "${RED}  [ERROR] Python 3.8+ required. Found: $PYTHON_VER${NC}"
    exit 1
fi

# Check ADB installation
echo ""
echo -e "${GREEN}[2/4] Checking Android Debug Bridge (ADB)...${NC}"
if command -v adb &> /dev/null; then
    ADB_VERSION=$(adb version 2>&1 | head -n 1)
    echo -e "  Found: $ADB_VERSION"
else
    echo -e "${YELLOW}  [WARNING] ADB not found!${NC}"
    echo -e "${YELLOW}  Install Android Platform Tools:${NC}"
    echo -e "${CYAN}  Ubuntu/Debian: sudo apt-get install android-tools-adb${NC}"
    echo -e "${CYAN}  macOS: brew install android-platform-tools${NC}"
    echo -e "${CYAN}  Or download from: https://developer.android.com/studio/releases/platform-tools${NC}"
    echo ""
    read -p "  Continue without ADB? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install Python dependencies
echo ""
echo -e "${GREEN}[3/4] Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "  Dependencies installed successfully!"
    else
        echo -e "${RED}  [ERROR] Failed to install dependencies${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  [WARNING] requirements.txt not found. Skipping...${NC}"
fi

# Create necessary directories
echo ""
echo -e "${GREEN}[4/4] Setting up project directories...${NC}"
DIRS=("logs" "output" "temp_data" "config")
for dir in "${DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo -e "  Created: $dir/"
    else
        echo -e "  Exists: $dir/"
    fi
done

# Make scripts executable
if [ -f "main.py" ]; then
    chmod +x main.py
fi

# Create default config if not exists
if [ ! -f "config/policy_config.json" ]; then
    echo -e "${YELLOW}  Creating default policy_config.json...${NC}"
    cat > config/policy_config.json << 'EOF'
{
  "adb_timeout": 30,
  "sms_policy": {
    "monitor_inbound": true,
    "monitor_outbound": true,
    "forbidden_keywords": ["classified", "confidential", "proprietary"],
    "log_all_messages": true
  },
  "contact_policy": {
    "max_personal_contacts": 50,
    "forbidden_domains": ["competitor.com"]
  },
  "location_policy": {
    "track_during_business_hours": true,
    "store_history_days": 30,
    "location_sample_interval_seconds": 300
  },
  "stealth": {"enabled": false},
  "reporting": {"output_format": "json", "generate_html_report": true}
}
EOF
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Connect your Android device via USB"
echo -e "2. Enable USB Debugging on device"
echo -e "3. Run: adb devices  (to verify connection)"
echo -e "4. Edit config/policy_config.json with your policies"
echo -e "5. Run: python3 main.py --full  (for complete extraction)"
echo ""
echo -e "${CYAN}For help: python3 main.py --help${NC}"
echo ""
