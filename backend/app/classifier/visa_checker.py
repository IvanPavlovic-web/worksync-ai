import re


VISA_POS = [
    r"\bvisa sponsorship\b", r"\bwe sponsor\b", r"\bsponsor(ing)? visas?\b",
    r"\brelocation support\b", r"\bwork permit\b", r"\bradna dozvola\b",
    r"\bwe help with relocation\b", r"\bblue card\b",
]
VISA_NEG = [
    r"\bno (visa )?sponsorship\b",
    r"\bmust have (existing )?work (permit|authorization)\b",
    r"\bwe (do not|don'?t) sponsor\b",
    r"\bmust be authorized to work\b",
    r"\bonly (us|eu) citizens\b",
    r"\bmust (be|have) (us|eu|uk) (citizen|work)\b",
]


def detect_visa_sponsorship(description: str) -> bool | None:
    """Vraća True/False/None (nepoznato)."""
    t = (description or "").lower()
    if any(re.search(p, t) for p in VISA_NEG):
        return False
    if any(re.search(p, t) for p in VISA_POS):
        return True
    return None