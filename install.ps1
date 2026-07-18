# BYOD Compliance Monitor - Windows Installation Script
# Run as Administrator for best results

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BYOD Compliance Monitor - Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as Administrator. Some features may not work." -ForegroundColor Yellow
    Write-Host ""
}

# Check Python installation
Write-Host "[1/4] Checking Python installation..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python not found! Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Red
    Write-Host "  Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    pause
    exit 1
}

# Check Python version
$version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$version -lt [version]"3.8") {
    Write-Host "  [ERROR] Python 3.8+ required. Found: $version" -ForegroundColor Red
    pause
    exit 1
}

# Check ADB installation
Write-Host ""
Write-Host "[2/4] Checking Android Debug Bridge (ADB)..." -ForegroundColor Green
$adbFound = Get-Command adb -ErrorAction SilentlyContinue
if ($adbFound) {
    $adbVersion = adb version 2>&1 | Select-Object -First 1
    Write-Host "  Found: $adbVersion" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] ADB not found in PATH!" -ForegroundColor Yellow
    Write-Host "  Download Android Platform Tools from:" -ForegroundColor Yellow
    Write-Host "  https://developer.android.com/studio/releases/platform-tools" -ForegroundColor Cyan
    Write-Host ""
    $installAdb = Read-Host "  Download and install ADB now? (y/n)"
    if ($installAdb -eq 'y') {
        Write-Host "  Downloading Android Platform Tools..." -ForegroundColor Green
        $adbUrl = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        $adbZip = "$env:TEMP\platform-tools.zip"
        
        try {
            Invoke-WebRequest -Uri $adbUrl -OutFile $adbZip
            Expand-Archive -Path $adbZip -DestinationPath "$env:LOCALAPPDATA\Android\platform-tools" -Force
            Remove-Item $adbZip
            
            # Add to PATH
            $adbPath = "$env:LOCALAPPDATA\Android\platform-tools"
            [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$adbPath", [EnvironmentVariableTarget]::User)
            $env:Path += ";$adbPath"
            
            Write-Host "  ADB installed successfully!" -ForegroundColor Green
            Write-Host "  Please restart your terminal for PATH changes to take effect." -ForegroundColor Yellow
        } catch {
            Write-Host "  [ERROR] Failed to download ADB. Please install manually." -ForegroundColor Red
        }
    }
}

# Install Python dependencies
Write-Host ""
Write-Host "[3/4] Installing Python dependencies..." -ForegroundColor Green
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Dependencies installed successfully!" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Failed to install dependencies" -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host "  [WARNING] requirements.txt not found. Skipping..." -ForegroundColor Yellow
}

# Create necessary directories
Write-Host ""
Write-Host "[4/4] Setting up project directories..." -ForegroundColor Green
$dirs = @("logs", "output", "temp_data", "config")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir/" -ForegroundColor Green
    } else {
        Write-Host "  Exists: $dir/" -ForegroundColor Cyan
    }
}

# Create default config if not exists
if (-not (Test-Path "config/policy_config.json")) {
    Write-Host "  Creating default policy_config.json..." -ForegroundColor Yellow
    $defaultConfig = @"
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
"@
    $defaultConfig | Out-File -FilePath "config/policy_config.json" -Encoding UTF8
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Connect your Android device via USB" -ForegroundColor White
Write-Host "2. Enable USB Debugging on device" -ForegroundColor White
Write-Host "3. Run: adb devices  (to verify connection)" -ForegroundColor White
Write-Host "4. Edit config/policy_config.json with your policies" -ForegroundColor White
Write-Host "5. Run: python main.py --full  (for complete extraction)" -ForegroundColor White
Write-Host ""
Write-Host "For help: python main.py --help" -ForegroundColor Cyan
Write-Host ""
pause
