“””
Contact Extractor Module

Extracts the complete contacts database from Android devices.

Android stores contacts in: 
/data/data/com.android.providers.contacts/databases/contacts2.db

This module pulls the database, parses all contact fields, and 
cross-references against compliance policies (forbidden domains, 
organization restrictions, personal contact limits for BYOD).

Key tables in contacts2.db:
- raw_contacts: Core contact records
- data: All contact data fields (phones, emails, orgs, etc.)
- mimetypes: Defines what each data row represents
- accounts: Contact sync accounts (Google, Exchange, etc.)
- groups: Contact groups/labels 
- """

import sqlite3 
import json 
import logging 
import shutil 
from pathlib import Path 
from datetime import datetime 
from typing import List, Dict, Any, Optional, Set, Tuple 
from dataclasses import dataclass, field

from .adb_interface import ADBInterface

logger = logging.getLogger(name)


@dataclass 
class Contact: 
""" 
Represents a single contact with all available fields.

Android contact storage is complex - one contact can have multiple
phone numbers, emails, and organization entries. This dataclass
consolidates all data points into a single contact record.
"""
contact_id: int
display_name: str
phone_numbers: List[Dict[str, str]] = field(default_factory=list)
email_addresses: List[Dict[str, str]] = field(default_factory=list)
organizations: List[Dict[str, str]] = field(default_factory=list)
photo_uri: Optional[str] = None
notes: Optional[str] = None
account_type: Optional[str] = None
last_modified: Optional[str] = None
is_starred: bool = False
raw_data: Dict[str, Any] = field(default_factory=dict)

@property
def primary_phone(self) -> Optional[str]:
    """Return the primary phone number if available."""
    if self.phone_numbers:
        for phone in self.phone_numbers:
            if phone.get("type") == "mobile":
                return phone["number"]
        return self.phone_numbers[0]["number"]
    return None

@property
def primary_email(self) -> Optional[str]:
    """Return the primary email address if available."""
    if self.email_addresses:
        for email in self.email_addresses:
            if email.get("type") == "work":
                return email["address"]
        return self.email_addresses[0]["address"]
    return None

@property
def email_domains(self) -> Set[str]:
    """Extract all email domains for compliance checking."""
    domains = set()
    for email in self.email_addresses:
        address = email.get("address", "")
        if "@" in address:
            domain = address.split("@")[1].lower()
            domains.add(domain)
    return domains

def to_dict(self) -> Dict[str, Any]:
    """Convert to dictionary for JSON serialization."""
    return {
        "contact_id": self.contact_id,
        "display_name": self.display_name,
        "phone_numbers": self.phone_numbers,
        "email_addresses": self.email_addresses,
        "organizations": self.organizations,
        "primary_phone": self.primary_phone,
        "primary_email": self.primary_email,
        "photo_uri": self.photo_uri,
        "account_type": self.account_type,
        "is_starred": self.is_starred
    }
class ContactExtractor: 
""" 
Extracts and parses contacts from Android devices.

Workflow:
1. Locate contacts2.db on the device
2. Pull it to local temporary storage
3. Parse all contact tables and consolidate data
4. Return structured Contact objects
5. Export for compliance reporting
"""

KNOWN_DB_PATHS = [
    "/data/data/com.android.providers.contacts/databases/contacts2.db",
    "/data/data/com.google.android.contacts/databases/contacts2.db",
    "/data/data/com.android.contacts/databases/contacts2.db",
]

CORPORATE_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "icloud.com", "aol.com", "proton.me", "mail.com"
}

PHONE_TYPE_MAP = {
    1: "home", 2: "mobile", 3: "work", 4: "work_fax",
    5: "home_fax", 6: "pager", 7: "other", 8: "callback",
    9: "car", 10: "company_main", 11: "isdn", 12: "main",
    13: "other_fax", 14: "radio", 15: "telex", 16: "tty_tdd",
    17: "work_mobile", 18: "work_pager", 19: "assistant", 20: "mms"
}

EMAIL_TYPE_MAP = {1: "home", 2: "work", 3: "other", 4: "mobile"}

def __init__(self, adb: ADBInterface, working_dir: str = "./temp_contacts"):
    """
    Initialize the contact extractor.
    
    Args:
        adb: Initialized ADBInterface for device communication
        working_dir: Local directory for temporary database storage
        
    Raises:
        ValueError: If adb is None or working_dir is invalid
    """
    if adb is None:
        raise ValueError("ADB interface cannot be None")
    
    self.adb = adb
    self.working_dir = Path(working_dir)
    self._validate_and_create_working_dir()

def _validate_and_create_working_dir(self) -> None:
    """Validate and create working directory."""
    try:
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify write permissions
        test_file = self.working_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        
    except (OSError, PermissionError) as e:
        logger.error(f"Cannot create or write to working directory: {e}")
        raise

def locate_database(self) -> Optional[str]:
    """
    Find the contacts2.db file on the device.
    
    Returns:
        Full path to the database, or None if not found
    """
    logger.info("Searching for contacts database...")
    
    try:
        # Try known paths first
        for path in self.KNOWN_DB_PATHS:
            if self._safe_check_file_exists(path):
                logger.info(f"Found contacts database at: {path}")
                return path
        
        # Dynamic search if standard paths fail
        logger.warning("Standard paths failed. Searching dynamically...")
        return self._dynamic_database_search()
        
    except Exception as e:
        logger.error(f"Error locating database: {e}")
        return None

def _safe_check_file_exists(self, path: str) -> bool:
    """Safely check if a file exists on the device."""
    try:
        return self.adb.file_exists(path)
    except Exception as e:
        logger.warning(f"Error checking file existence for {path}: {e}")
        return False

def _dynamic_database_search(self) -> Optional[str]:
    """Dynamically search for contacts database."""
    try:
        search_cmd = "find /data/data/ -name 'contacts2.db' -type f 2>/dev/null | head -1"
        output = self.adb.shell_command(search_cmd, as_root=True)
        
        if output and output.strip():
            path = output.strip().split('\n')[0].strip()
            if path:
                logger.info(f"Found via search: {path}")
                return path
        
        logger.error("Could not locate contacts database")
        return None
        
    except Exception as e:
        logger.error(f"Dynamic search failed: {e}")
        return None

def extract_database(self, db_path: str) -> Optional[Path]:
    """
    Pull the contacts database from device to local storage.
    
    Args:
        db_path: Full path on device
        
    Returns:
        Path to local copy, or None if extraction failed
        
    Raises:
        ValueError: If db_path is empty or None
    """
    if not db_path:
        raise ValueError("Database path cannot be empty")
    
    local_path = self.working_dir / "contacts2_extracted.db"
    temp_remote = "/sdcard/contacts2_temp.db"
    
    try:
        # Remove any existing temp file
        self.adb.shell_command(f"rm -f {temp_remote}")
        
        # Step 1: Copy to accessible location
        logger.info(f"Copying {db_path} to {temp_remote}...")
        if not self._copy_database_to_temp(db_path, temp_remote):
            return None
        
        # Step 2: Pull to local
        logger.info(f"Pulling to {local_path}...")
        if not self._pull_database_from_temp(temp_remote, local_path):
            return None
        
        logger.info(f"Database extracted: {local_path.stat().st_size} bytes")
        return local_path
        
    except Exception as e:
        logger.error(f"Database extraction failed: {e}")
        return None
        
    finally:
        # Step 3: Clean up temp file
        try:
            self.adb.shell_command(f"rm -f {temp_remote}")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file: {e}")

def _copy_database_to_temp(self, db_path: str, temp_remote: str) -> bool:
    """Copy database to accessible location on device."""
    try:
        # Try with root first
        copy_cmd = f"su -c 'cp {db_path} {temp_remote}'"
        result = self.adb.shell_command(copy_cmd, as_root=False)
        
        if "Permission denied" in result or "not found" in result.lower():
            # Try without root
            copy_cmd = f"cp {db_path} {temp_remote}"
            result = self.adb.shell_command(copy_cmd)
            
            if "Permission denied" in result:
                logger.error("Permission denied. Device may need root access.")
                return False
        
        # Verify the copy was successful
        verify_cmd = f"test -f {temp_remote} && echo 'exists'"
        verify_result = self.adb.shell_command(verify_cmd)
        
        if "exists" not in verify_result:
            logger.error("Database copy verification failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to copy database to temp location: {e}")
        return False

def _pull_database_from_temp(self, temp_remote: str, local_path: Path) -> bool:
    """Pull database from temp location to local storage."""
    try:
        success = self.adb.pull_file(temp_remote, str(local_path))
        
        if not success:
            logger.error("Failed to pull database file")
            return False
        
        if not local_path.exists():
            logger.error("Pulled file does not exist locally")
            return False
        
        if local_path.stat().st_size == 0:
            logger.error("Pulled file is empty")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to pull database: {e}")
        return False

def parse_contacts(self, db_path: Path) -> List[Contact]:
    """
    Parse all contacts from the extracted database.
    
    Args:
        db_path: Path to local contacts2.db
        
    Returns:
        List of Contact objects
    """
    if not db_path or not db_path.exists():
        logger.error(f"Database file does not exist: {db_path}")
        return []
    
    logger.info("Parsing contacts database...")
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrent access
        conn.execute("PRAGMA journal_mode=WAL")
        
        contacts_dict = self._parse_raw_contacts(conn)
        
        if contacts_dict:
            self._parse_phone_numbers(conn, contacts_dict)
            self._parse_emails(conn, contacts_dict)
            self._parse_organizations(conn, contacts_dict)
            self._parse_photos(conn, contacts_dict)
        
        conn.close()
        
        contacts_list = list(contacts_dict.values())
        contacts_list.sort(key=lambda c: c.display_name.lower() if c.display_name else "")
        
        self._log_parsing_summary(contacts_list)
        
        return contacts_list
        
    except sqlite3.Error as e:
        logger.error(f"Database error while parsing contacts: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while parsing contacts: {e}")
        return []

def _parse_raw_contacts(self, conn: sqlite3.Connection) -> Dict[int, Contact]:
    """Parse raw contacts from the database."""
    contacts_dict = {}
    cursor = conn.cursor()
    
    try:
        # Validate table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='raw_contacts'")
        if not cursor.fetchone():
            logger.error("raw_contacts table not found")
            return contacts_dict
        
        cursor.execute("""
            SELECT 
                _id,
                display_name,
                account_type,
                starred,
                last_time_contacted
            FROM raw_contacts
            WHERE deleted = 0
            ORDER BY display_name
        """)
        
        for row in cursor.fetchall():
            contact_id = row["_id"]
            display_name = row["display_name"] or f"Unknown_{contact_id}"
            
            contact = Contact(
                contact_id=contact_id,
                display_name=display_name,
                account_type=row["account_type"],
                is_starred=bool(row["starred"])
            )
            contacts_dict[contact_id] = contact
        
        logger.info(f"Found {len(contacts_dict)} raw contacts")
        
    except sqlite3.Error as e:
        logger.error(f"Error parsing raw contacts: {e}")
    finally:
        cursor.close()
    
    return contacts_dict

def _parse_phone_numbers(self, conn: sqlite3.Connection, contacts_dict: Dict[int, Contact]) -> None:
    """Parse phone numbers from the data table."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                d.raw_contact_id,
                d.data1 AS phone_number,
                d.data2 AS phone_type,
                d.data3 AS label
            FROM data d
            INNER JOIN mimetypes m ON d.mimetype_id = m._id
            WHERE m.mimetype = 'vnd.android.cursor.item/phone_v2'
                AND d.data1 IS NOT NULL
                AND d.data1 != ''
        """)
        
        for row in cursor.fetchall():
            contact_id = row["raw_contact_id"]
            if contact_id in contacts_dict:
                phone_type = self._get_phone_type_label(row["phone_type"])
                contacts_dict[contact_id].phone_numbers.append({
                    "number": row["phone_number"].strip(),
                    "type": phone_type,
                    "label": row["label"] or phone_type
                })
                
    except sqlite3.Error as e:
        logger.error(f"Error parsing phone numbers: {e}")
    finally:
        cursor.close()

def _parse_emails(self, conn: sqlite3.Connection, contacts_dict: Dict[int, Contact]) -> None:
    """Parse email addresses from the data table."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                d.raw_contact_id,
                d.data1 AS email_address,
                d.data2 AS email_type,
                d.data3 AS label
            FROM data d
            INNER JOIN mimetypes m ON d.mimetype_id = m._id
            WHERE m.mimetype = 'vnd.android.cursor.item/email_v2'
                AND d.data1 IS NOT NULL
                AND d.data1 != ''
        """)
        
        for row in cursor.fetchall():
            contact_id = row["raw_contact_id"]
            if contact_id in contacts_dict:
                email_type = self._get_email_type_label(row["email_type"])
                contacts_dict[contact_id].email_addresses.append({
                    "address": row["email_address"].strip().lower(),
                    "type": email_type,
                    "label": row["label"] or email_type
                })
                
    except sqlite3.Error as e:
        logger.error(f"Error parsing emails: {e}")
    finally:
        cursor.close()

def _parse_organizations(self, conn: sqlite3.Connection, contacts_dict: Dict[int, Contact]) -> None:
    """Parse organization information from the data table."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                d.raw_contact_id,
                d.data1 AS company,
                d.data4 AS title
            FROM data d
            INNER JOIN mimetypes m ON d.mimetype_id = m._id
            WHERE m.mimetype = 'vnd.android.cursor.item/organization'
        """)
        
        for row in cursor.fetchall():
            contact_id = row["raw_contact_id"]
            if contact_id in contacts_dict:
                contacts_dict[contact_id].organizations.append({
                    "company": (row["company"] or "").strip(),
                    "title": (row["title"] or "").strip()
                })
                
    except sqlite3.Error as e:
        logger.error(f"Error parsing organizations: {e}")
    finally:
        cursor.close()

def _parse_photos(self, conn: sqlite3.Connection, contacts_dict: Dict[int, Contact]) -> None:
    """Parse photo URIs from the data table."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                d.raw_contact_id,
                d.data15 AS photo_uri
            FROM data d
            INNER JOIN mimetypes m ON d.mimetype_id = m._id
            WHERE m.mimetype = 'vnd.android.cursor.item/photo'
                AND d.data15 IS NOT NULL
        """)
        
        for row in cursor.fetchall():
            contact_id = row["raw_contact_id"]
            if contact_id in contacts_dict:
                contacts_dict[contact_id].photo_uri = row["photo_uri"]
                
    except sqlite3.Error as e:
        logger.error(f"Error parsing photos: {e}")
    finally:
        cursor.close()

def _log_parsing_summary(self, contacts_list: List[Contact]) -> None:
    """Log summary statistics of parsed contacts."""
    logger.info(f"Parsed {len(contacts_list)} contacts with full details")
    logger.info(f"  - With phone numbers: {sum(1 for c in contacts_list if c.phone_numbers)}")
    logger.info(f"  - With emails: {sum(1 for c in contacts_list if c.email_addresses)}")
    logger.info(f"  - With organizations: {sum(1 for c in contacts_list if c.organizations)}")

def _get_phone_type_label(self, type_code: Any) -> str:
    """Convert Android phone type code to human-readable label."""
    if type_code is None:
        return "other"
    
    try:
        return self.PHONE_TYPE_MAP.get(int(type_code), "other")
    except (ValueError, TypeError):
        return "custom"

def _get_email_type_label(self, type_code: Any) -> str:
    """Convert Android email type code to human-readable label."""
    if type_code is None:
        return "other"
    
    try:
        return self.EMAIL_TYPE_MAP.get(int(type_code), "other")
    except (ValueError, TypeError):
        return "custom"

def extract_all(self) -> List[Contact]:
    """
    Run the complete contact extraction pipeline.
    
    Returns:
        List of Contact objects
    """
    logger.info("Starting full contact extraction pipeline")
    
    try:
        db_path = self.locate_database()
        if not db_path:
            logger.error("Cannot proceed: contacts database not found")
            return []
        
        local_db = self.extract_database(db_path)
        if not local_db:
            logger.error("Cannot proceed: database extraction failed")
            return []
        
        contacts = self.parse_contacts(local_db)
        
        # Clean up local database after parsing
        self._cleanup_local_db(local_db)
        
        logger.info(f"Contact extraction complete: {len(contacts)} contacts")
        return contacts
        
    except Exception as e:
        logger.error(f"Contact extraction pipeline failed: {e}")
        return []

def _cleanup_local_db(self, db_path: Path) -> None:
    """Clean up local database files."""
    try:
        if db_path and db_path.exists():
            db_path.unlink()
            logger.debug(f"Cleaned up local database: {db_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up local database: {e}")

def cleanup(self) -> None:
    """Clean up all temporary files and working directory."""
    try:
        if self.working_dir.exists():
            shutil.rmtree(self.working_dir)
            logger.info(f"Cleaned up working directory: {self.working_dir}")
    except Exception as e:
        logger.warning(f"Failed to clean up working directory: {e}")

def filter_by_domain(self, contacts: List[Contact], domain: str) -> List[Contact]:
    """
    Filter contacts by email domain (for compliance checking).
    
    Args:
        contacts: List of contacts to filter
        domain: Domain to filter by (e.g., 'competitor.com')
        
    Returns:
        Contacts with emails at the specified domain
    """
    if not domain:
        logger.warning("Empty domain filter provided")
        return contacts
    
    domain = domain.lower().strip()
    return [
        c for c in contacts
        if domain in c.email_domains
    ]

def filter_by_organization(self, contacts: List[Contact], org_name: str) -> List[Contact]:
    """
    Filter contacts by organization name.
    
    Args:
        contacts: List of contacts to filter
        org_name: Organization name to search for
        
    Returns:
        Contacts associated with the specified organization
    """
    if not org_name:
        logger.warning("Empty organization filter provided")
        return contacts
    
    org_name_lower = org_name.lower().strip()
    return [
        c for c in contacts
        if any(org_name_lower in org.get("company", "").lower() 
              for org in c.organizations)
    ]

def count_personal_contacts(self, contacts: List[Contact]) -> int:
    """
    Count contacts that appear to be personal (non-corporate).
    
    Heuristic: Contacts without organization info and with
    non-corporate email domains are likely personal.
    
    Args:
        contacts: List of contacts to analyze
        
    Returns:
        Estimated count of personal contacts
    """
    personal_count = 0
    for contact in contacts:
        is_corporate = bool(contact.organizations)
        has_corporate_email = any(
            domain not in self.CORPORATE_DOMAINS
            for domain in contact.email_domains
        )
        
        if not is_corporate and not has_corporate_email:
            personal_count += 1
    
    return personal_count

def export_to_json(self, contacts: List[Contact], output_path: str = "contacts_export.json") -> None:
    """
    Export contacts to JSON for reporting.
    
    Args:
        contacts: List of Contact objects
        output_path: Destination file path
        
    Raises:
        IOError: If unable to write to output path
    """
    if not output_path:
        raise ValueError("Output path cannot be empty")
    
    try:
        export_data = {
            "extraction_timestamp": datetime.now().isoformat(),
            "device_serial": self.adb.device_serial,
            "total_contacts": len(contacts),
            "contacts": [c.to_dict() for c in contacts]
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Contacts exported to {output_path}")
        
    except IOError as e:
        logger.error(f"Failed to write export file: {e}")
        raise
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise

def __del__(self):
    """Destructor to ensure cleanup on object destruction."""
    self.cleanup()

