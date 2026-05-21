"""
Seed script: inserts sample alerts into the database.
Run once with:  python seed.py
Safe to re-run: it clears existing alerts first so you don't get duplicates.
"""

from database import SessionLocal, engine, Base
import models

# Make sure the table exists before we try to insert into it.
Base.metadata.create_all(bind=engine)

# 20+ realistic sample alerts covering a spread of
# severities, statuses, and sources (good for the Day 3 dashboard).
sample_alerts = [
    {"title": "Suspicious login attempt", "description": "Multiple failed logins from an unknown IP in Eastern Europe.", "severity": "High", "status": "Open", "source": "SIEM"},
    {"title": "Malware detected on endpoint", "description": "Trojan signature found on workstation WS-0421.", "severity": "Critical", "status": "In Progress", "source": "Endpoint"},
    {"title": "Phishing email reported", "description": "User reported a phishing email impersonating the IT helpdesk.", "severity": "Medium", "status": "Open", "source": "Email"},
    {"title": "Firewall blocked port scan", "description": "Sequential port scan blocked from external host 203.0.113.5.", "severity": "Low", "status": "Closed", "source": "Firewall"},
    {"title": "Unusual cloud API usage", "description": "Spike in S3 access requests from an unrecognized region.", "severity": "High", "status": "Open", "source": "Cloud"},
    {"title": "Brute force on VPN gateway", "description": "Repeated authentication failures against the corporate VPN.", "severity": "High", "status": "In Progress", "source": "Firewall"},
    {"title": "Outdated TLS certificate", "description": "Public web server presenting an expired TLS certificate.", "severity": "Low", "status": "Open", "source": "Cloud"},
    {"title": "Ransomware behavior flagged", "description": "Mass file-rename activity consistent with ransomware on FS-02.", "severity": "Critical", "status": "Open", "source": "Endpoint"},
    {"title": "Suspicious PowerShell execution", "description": "Encoded PowerShell command launched by a non-admin user.", "severity": "High", "status": "In Progress", "source": "Endpoint"},
    {"title": "Data exfiltration attempt", "description": "Large outbound transfer to an unknown file-sharing domain.", "severity": "Critical", "status": "Open", "source": "SIEM"},
    {"title": "Spam campaign detected", "description": "Bulk spam emails sent from a compromised internal mailbox.", "severity": "Medium", "status": "Closed", "source": "Email"},
    {"title": "New admin account created", "description": "Unexpected privileged account created outside change window.", "severity": "High", "status": "Open", "source": "Cloud"},
    {"title": "Port 3389 exposed publicly", "description": "RDP found open to the internet on host SRV-DMZ-07.", "severity": "Medium", "status": "In Progress", "source": "Firewall"},
    {"title": "Failed antivirus update", "description": "Endpoint protection failed to update on 14 machines.", "severity": "Low", "status": "Open", "source": "Endpoint"},
    {"title": "Geo-impossible login", "description": "Logins from two countries within five minutes for one user.", "severity": "High", "status": "Open", "source": "SIEM"},
    {"title": "Misconfigured storage bucket", "description": "Cloud storage bucket set to public-read unexpectedly.", "severity": "Medium", "status": "Closed", "source": "Cloud"},
    {"title": "Suspicious email attachment", "description": "Macro-enabled document attached to an external email.", "severity": "Medium", "status": "Open", "source": "Email"},
    {"title": "Lateral movement detected", "description": "Internal host scanning multiple servers on SMB ports.", "severity": "Critical", "status": "In Progress", "source": "SIEM"},
    {"title": "Disabled security agent", "description": "Endpoint security agent stopped on workstation WS-0188.", "severity": "High", "status": "Open", "source": "Endpoint"},
    {"title": "DNS tunneling suspected", "description": "Abnormally large volume of TXT DNS queries to one domain.", "severity": "High", "status": "Open", "source": "Firewall"},
    {"title": "Weak password policy alert", "description": "Several accounts found using passwords below policy length.", "severity": "Low", "status": "Closed", "source": "Cloud"},
    {"title": "Account lockout storm", "description": "Dozens of accounts locked out within a short time window.", "severity": "Medium", "status": "In Progress", "source": "SIEM"},
]


def seed():
    db = SessionLocal()
    try:
        # Clear existing rows first so re-running doesn't pile up duplicates.
        deleted = db.query(models.Alert).delete()
        db.commit()

        # Insert all the sample alerts.
        for data in sample_alerts:
            alert = models.Alert(**data)
            db.add(alert)
        db.commit()

        count = db.query(models.Alert).count()
        print(f"Cleared {deleted} old alert(s). Seeded {count} alerts.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()