# 🔍 BUG HUNTING FRAMEWORK - Automated Detection & Logging
# HUNT.ZA Hackathon - Universal Acceptance Bug Hunt

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# ============================================================
# EMAIL VALIDATOR (Custom - No external libs)
# ============================================================

def validate_email(email: str) -> bool:
    """Validates email with support for new TLDs (.africa, .joburg, .capetown)"""
    pattern = r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip()
    
    if email.count('@') != 1:
        return False
    
    if not re.match(pattern, email):
        return False
    
    local, domain = email.rsplit('@', 1)
    
    if local.startswith('.') or local.endswith('.'):
        return False
    if local.startswith('+') or local.endswith('+'):
        return False
    
    if domain.startswith('-') or domain.startswith('.'):
        return False
    if domain.endswith('-') or domain.endswith('.'):
        return False
    
    if '.' not in domain:
        return False
    
    domain_parts = domain.split('.')
    tld = domain_parts[-1]
    
    if len(tld) < 2:
        return False
    
    if not tld.isalpha():
        return False
    
    return True


# ============================================================
# BUG DETECTION & LOGGING
# ============================================================

class BugReport:
    """Represents a single bug finding"""
    
    def __init__(
        self,
        bug_id: str,
        website_name: str,
        website_url: str,
        form_type: str,
        test_email: str,
        test_person: str,
        domain_name: str,
        error_message: str,
        validation_logic: str,
        severity: str = "HIGH",
        timestamp: Optional[str] = None
    ):
        self.bug_id = bug_id
        self.website_name = website_name
        self.website_url = website_url
        self.form_type = form_type
        self.test_email = test_email
        self.test_person = test_person
        self.domain_name = domain_name
        self.error_message = error_message
        self.validation_logic = validation_logic
        self.severity = severity
        self.timestamp = timestamp or datetime.now().isoformat()
        
        # Validate that email SHOULD be valid
        self.should_be_valid = validate_email(test_email)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON logging"""
        return {
            'bug_id': self.bug_id,
            'website_name': self.website_name,
            'website_url': self.website_url,
            'form_type': self.form_type,
            'test_email': self.test_email,
            'test_person': self.test_person,
            'domain_name': self.domain_name,
            'error_message': self.error_message,
            'validation_logic': self.validation_logic,
            'severity': self.severity,
            'timestamp': self.timestamp,
            'email_should_be_valid': self.should_be_valid,
            'is_ua_compliance_failure': True  # All these are UA failures
        }
    
    def to_markdown(self) -> str:
        """Convert to markdown for human-readable reports"""
        return f"""
## Bug #{self.bug_id}: {self.website_name}

**Website**: {self.website_name}  
**URL**: {self.website_url}  
**Form Type**: {self.form_type}  
**Tester**: {self.test_person}  
**Timestamp**: {self.timestamp}  

### Test Details
- **Email Tested**: `{self.test_email}`
- **Domain Name**: `.{self.domain_name}`
- **Email Valid?**: {self.should_be_valid}
- **Website Response**: {self.error_message}

### Root Cause Analysis
**Validation Logic Found**: {self.validation_logic}

### Impact
- **Severity**: {self.severity}
- **Affected Users**: All users with `.{self.domain_name}` email addresses
- **Type**: Universal Acceptance (UA) Compliance Failure

### Recommendation
Update email validation to support longer TLDs (minimum 2-8+ characters).

Change from: `[a-z]{{2,3}}` (limits to 2-3 characters)  
Change to: `[a-z]{{2,}}` (supports 2+ characters)

This would enable support for:
- `.africa` (6 characters)
- `.joburg` (6 characters)  
- `.capetown` (8 characters)

---
"""


class BugHuntingSession:
    """Manages a complete bug hunting session"""
    
    def __init__(self, session_name: str = "HUNT.ZA"):
        self.session_name = session_name
        self.bugs: List[BugReport] = []
        self.bug_counter = 0
    
    def add_bug(
        self,
        website_name: str,
        website_url: str,
        form_type: str,
        test_email: str,
        test_person: str,
        domain_name: str,
        error_message: str,
        validation_logic: str,
        severity: str = "HIGH"
    ) -> BugReport:
        """Add a new bug to the report"""
        self.bug_counter += 1
        bug_id = f"BUG-{str(self.bug_counter).zfill(3)}"
        
        bug = BugReport(
            bug_id=bug_id,
            website_name=website_name,
            website_url=website_url,
            form_type=form_type,
            test_email=test_email,
            test_person=test_person,
            domain_name=domain_name,
            error_message=error_message,
            validation_logic=validation_logic,
            severity=severity
        )
        
        self.bugs.append(bug)
        return bug
    
    def export_json(self, filename: str = "bug_report.json"):
        """Export all bugs as JSON"""
        data = {
            'session': self.session_name,
            'timestamp': datetime.now().isoformat(),
            'total_bugs_found': len(self.bugs),
            'bugs': [bug.to_dict() for bug in self.bugs]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename
    
    def export_markdown(self, filename: str = "BUG_REPORT.md"):
        """Export all bugs as formatted markdown"""
        content = f"""# HUNT.ZA Bug Report

**Session**: {self.session_name}  
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Bugs Found**: {len(self.bugs)}  

---

"""
        
        for bug in self.bugs:
            content += bug.to_markdown()
        
        # Add summary
        content += """
---

## Summary

All bugs found are **Universal Acceptance (UA) Compliance Failures**.

These websites reject valid email addresses on new ICANN-approved TLDs:
- `.africa`
- `.joburg`
- `.capetown`

### Common Root Causes

1. **Regex Pattern Too Restrictive**: `{2,3}` limits TLDs to 2-3 characters
2. **Hardcoded TLD Lists**: Only whitelist `.com`, `.net`, `.org`, etc.
3. **Outdated Validation Libraries**: Email validators that don't support new TLDs

### Impact

Users with `.africa`, `.joburg`, or `.capetown` email addresses cannot:
- Sign up for accounts
- Login to systems
- Complete transactions
- Access government services

This directly violates ICANN's Universal Acceptance standards.

### Recommendations

1. Update regex patterns to support 2+ character TLDs
2. Remove hardcoded TLD whitelists
3. Use RFC 5322 compliant validation
4. Test with new TLD email addresses

---

## Test Cases Used

```
Email Format: [username]@[company].[domain]

Domains Tested:
- .africa (6 characters)
- .joburg (6 characters)
- .capetown (8 characters)

Testers:
- NTU
- LINDO
- LUAN
```

"""
        
        with open(filename, 'w') as f:
            f.write(content)
        
        return filename
    
    def print_summary(self):
        """Print a summary of all found bugs"""
        print("\n" + "="*70)
        print(f"📊 BUG HUNTING SESSION SUMMARY - {self.session_name}")
        print("="*70)
        print(f"\nTotal bugs found: {len(self.bugs)}\n")
        
        for bug in self.bugs:
            print(f"🐛 {bug.bug_id}: {bug.website_name}")
            print(f"   Email: {bug.test_email}")
            print(f"   Tester: {bug.test_person}")
            print(f"   Error: {bug.error_message}")
            print(f"   Root Cause: {bug.validation_logic}")
            print()


# ============================================================
# SAMPLE BUG DATA - READY TO ADD YOUR FINDINGS
# ============================================================

def create_sample_bugs():
    """Create sample bugs for demonstration"""
    session = BugHuntingSession("HUNT.ZA - 20 June 2026")
    
    # Sample bugs (replace with actual findings)
    bugs_to_add = [
        {
            'website_name': 'ABSA Bank Online',
            'website_url': 'https://www.absa.co.za/login',
            'form_type': 'Login Form',
            'test_email': 'lindo@company.africa',
            'test_person': 'LINDO',
            'domain_name': 'africa',
            'error_message': 'Please enter a valid email address',
            'validation_logic': 'Regex pattern: [a-z0-9]+@[a-z0-9]+\\.[a-z]{2,3}$ (Max 3 char TLD)',
        },
        {
            'website_name': 'Johannesburg City Portal',
            'website_url': 'https://www.joburg.org.za/register',
            'form_type': 'Account Registration',
            'test_email': 'luan@company.joburg',
            'test_person': 'LUAN',
            'domain_name': 'joburg',
            'error_message': 'Invalid email domain. Only standard domains accepted.',
            'validation_logic': 'Hardcoded domain list: com, net, org, co.za (missing .joburg)',
        },
        {
            'website_name': 'Cape Town Municipality Services',
            'website_url': 'https://services.capetown.gov.za/apply',
            'form_type': 'Service Application',
            'test_email': 'ntu@test.capetown',
            'test_person': 'NTU',
            'domain_name': 'capetown',
            'error_message': 'TLD not recognized by system',
            'validation_logic': 'Backend API rejects TLDs with more than 6 characters',
        },
    ]
    
    for bug_data in bugs_to_add:
        session.add_bug(**bug_data)
    
    return session


# ============================================================
# INTERACTIVE BUG LOGGING SYSTEM
# ============================================================

def log_bug_interactive():
    """Interactive prompt to log a bug"""
    session = BugHuntingSession("HUNT.ZA - 20 June 2026")
    
    while True:
        print("\n" + "="*70)
        print("🐛 LOG A NEW BUG")
        print("="*70)
        
        website_name = input("Website name: ").strip()
        if not website_name:
            break
        
        website_url = input("Website URL: ").strip()
        form_type = input("Form type (Login/Signup/Contact/etc): ").strip()
        test_email = input("Email tested (e.g., user@company.africa): ").strip()
        test_person = input("Tester name (NTU/LINDO/LUAN): ").strip()
        domain_name = input("Domain name tested (africa/joburg/capetown): ").strip()
        error_message = input("Error message shown: ").strip()
        validation_logic = input("Root cause (what validation failed): ").strip()
        
        # Add the bug
        session.add_bug(
            website_name=website_name,
            website_url=website_url,
            form_type=form_type,
            test_email=test_email,
            test_person=test_person,
            domain_name=domain_name,
            error_message=error_message,
            validation_logic=validation_logic,
            severity="HIGH"
        )
        
        print(f"\n✅ Bug logged successfully!")
        print(f"Continue logging? (Enter website name or press Ctrl+C to exit)")
    
    return session


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔍 HUNT.ZA BUG HUNTING FRAMEWORK")
    print("="*70)
    print("\nOptions:")
    print("1. View sample bugs")
    print("2. Log bugs interactively")
    print("3. Export sample report\n")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        # Show sample bugs
        session = create_sample_bugs()
        session.print_summary()
        
        # Export
        json_file = session.export_json("bugs.json")
        md_file = session.export_markdown("BUG_REPORT.md")
        
        print(f"\n✅ Exported to:")
        print(f"   - {json_file}")
        print(f"   - {md_file}\n")
    
    elif choice == "2":
        # Interactive logging
        session = log_bug_interactive()
        session.print_summary()
        
        # Export
        json_file = session.export_json("bugs.json")
        md_file = session.export_markdown("BUG_REPORT.md")
        
        print(f"\n✅ Exported to:")
        print(f"   - {json_file}")
        print(f"   - {md_file}\n")
    
    elif choice == "3":
        # Just export sample
        session = create_sample_bugs()
        json_file = session.export_json("bugs.json")
        md_file = session.export_markdown("BUG_REPORT.md")
        
        print(f"\n✅ Sample report exported to:")
        print(f"   - {json_file}")
        print(f"   - {md_file}\n")
    
    else:
        print("Invalid option")