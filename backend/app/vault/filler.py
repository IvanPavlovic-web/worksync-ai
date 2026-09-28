import re

from app.models import ProfileVault


# Regex (bez ^ i $) → naziv polja u ProfileVault
FIELD_MAP: dict[str, str | tuple] = {
    r"first[\s_]?name": "first_name",
    r"last[\s_]?name|surname|family[\s_]?name": "last_name",
    r"full[\s_]?name|your[\s_]?name|ime i prezime": ("concat", ["first_name", "last_name"]),
    r"^email|e-?mail": "email",
    r"phone|mobile|telefon|tel\b": "phone",
    r"linkedin": "linkedin_url",
    r"github": "github_url",
    r"portfolio|personal[\s_]?website|web[\s_]?site": "portfolio_url",
    r"twitter|x\.com": "twitter_url",
    r"\bcity\b|town|grad": "city",
    r"postal|zip|poštanski": "postal_code",
    r"state|province|region|kanton": "state_region",
    r"country|država|zemlja": "country",
    r"address.*1|street|ulica": "address_line1",
    r"address.*2|apt|suite|stan": "address_line2",
    r"salary|compensation|plata": "desired_salary",
    r"notice[\s_]?period": "notice_period_days",
    r"sponsor": "requires_sponsorship",
    r"relocat|selidb": "willing_to_relocate",
    r"how[\s_]?did[\s_]?you[\s_]?hear": "how_did_you_hear",
    r"gender|spol": "gender",
    r"veteran": "veteran_status",
    r"disab": "disability_status",
    r"ethnic|race": "ethnicity",
}


def guess_value(label: str, field_name: str, vault: ProfileVault):
    """Pokušaj naći vrijednost iz vault-a na osnovu labele ili name atributa."""
    hay = f"{label} {field_name}".lower()

    for pattern, field in FIELD_MAP.items():
        if re.search(pattern, hay, re.IGNORECASE):
            if isinstance(field, tuple) and field[0] == "concat":
                parts = [getattr(vault, f, None) for f in field[1]]
                return " ".join(p for p in parts if p)
            val = getattr(vault, field, None)
            if val is not None:
                return val

    # Fallback: custom_fields
    if vault.custom_fields:
        for k, v in vault.custom_fields.items():
            if k.lower() in hay:
                return v

    return None


def vault_to_autofill_dict(vault: ProfileVault) -> dict:
    """Za Playwright autofill — sve na jednom mjestu."""
    return {
        "first_name": vault.first_name or "",
        "last_name": vault.last_name or "",
        "full_name": f"{vault.first_name or ''} {vault.last_name or ''}".strip(),
        "email": vault.email or "",
        "phone": vault.phone or "",
        "phone_country_code": vault.phone_country_code or "",
        "linkedin_url": vault.linkedin_url or "",
        "github_url": vault.github_url or "",
        "portfolio_url": vault.portfolio_url or "",
        "city": vault.city or "",
        "country": vault.country or "",
        "country_code": vault.country_code or "",
        "postal_code": vault.postal_code or "",
        "address_line1": vault.address_line1 or "",
        "address_line2": vault.address_line2 or "",
        "resume_url": vault.resume_url or "",
        "requires_sponsorship": vault.requires_sponsorship,
        "willing_to_relocate": vault.willing_to_relocate,
        "desired_salary": str(vault.desired_salary) if vault.desired_salary else "",
        "notice_period_days": str(vault.notice_period_days) if vault.notice_period_days else "",
    }