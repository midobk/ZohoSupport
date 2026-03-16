ZOHO_SOURCES = [
    {
        "id": "kb-101",
        "title": "Reset Multi-Factor Authentication for Locked Users",
        "summary": "Admin flow to verify identity and reset MFA in Zoho Directory.",
        "url": "https://help.zoho.com/portal/en/kb/accounts/security/mfa-reset",
    },
    {
        "id": "kb-204",
        "title": "Troubleshooting Login Challenges",
        "summary": "Checklist for OTP delay, device mismatch, and account lock scenarios.",
        "url": "https://help.zoho.com/portal/en/kb/accounts/login-troubleshooting",
    },
]

MOCK_TICKETS = [
    {
        "ticketId": "TCK-4401",
        "subject": "User unable to login after phone replacement",
        "confidence": 0.91,
        "snippet": "Customer replaced phone and cannot generate authenticator codes.",
        "resolution": "Verified identity and re-bound MFA to new device.",
    },
    {
        "ticketId": "TCK-4387",
        "subject": "MFA reset required for locked account",
        "confidence": 0.88,
        "snippet": "Account was locked after 5 failed OTP attempts.",
        "resolution": "Support admin reset MFA and user regained access.",
    },
    {
        "ticketId": "TCK-4210",
        "subject": "Delayed OTP for EU region users",
        "confidence": 0.73,
        "snippet": "OTP reached user after expiration in multiple attempts.",
        "resolution": "Switched to backup channel and advised time-sync update.",
    },
]
