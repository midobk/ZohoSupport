ZOHO_SOURCES = [
    {
        "id": "kb-101",
        "title": "Reset Multi-Factor Authentication for Locked Users",
        "snippet": "Verify requester identity, revoke old factors, and force re-enrollment from a trusted device.",
        "url": "https://help.zoho.com/portal/en/kb/accounts/security/mfa-reset",
        "sourceType": "OfficialKB",
        "trustLabel": "Verified",
    },
    {
        "id": "kb-204",
        "title": "Troubleshooting Login Challenges",
        "snippet": "Use this checklist for delayed OTPs, mismatched authenticator apps, and temporary lockouts.",
        "url": "https://help.zoho.com/portal/en/kb/accounts/login-troubleshooting",
        "sourceType": "OfficialKB",
        "trustLabel": "Verified",
    },
    {
        "id": "kb-322",
        "title": "Account Recovery and Sign-in Verification Best Practices",
        "snippet": "Escalation criteria and communication template for users who cannot complete MFA.",
        "url": "https://help.zoho.com/portal/en/kb/accounts/recovery/sign-in-verification",
        "sourceType": "OfficialKB",
        "trustLabel": "Verified",
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
