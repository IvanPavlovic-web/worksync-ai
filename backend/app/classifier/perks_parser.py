import re


PERKS = {
    "housing_provided": [
        r"\b(smještaj|accommodation|housing|unterkunft|wohnung)\b.*\b(provided|osiguran|free|besplat)",
        r"\bslobodan smještaj\b", r"\bfree housing\b",
    ],
    "relocation_support": [
        r"\brelocation (package|support|assistance)\b",
        r"\bpomoć pri selidbi\b", r"\brelocat(ion)? bonus\b",
    ],
    "visa_sponsorship": [
        r"\bvisa sponsorship\b", r"\bwe sponsor visas\b",
        r"\bradna dozvola\b", r"\bsponsor(ing)? (a )?visa\b",
    ],
    "meal_provided": [
        r"\b(obroci|meal|verpflegung|hrana)\b.*\b(provided|osiguran|free|besplat)",
        r"\bfree meals\b",
    ],
    "language_course": [
        r"\b(german|jezički|sprachkurs) course\b",
        r"\bnjemački kurs\b",
    ],
    "vehicle_provided": [
        r"\b(company car|vozilo|auto)\b.*\b(provided|osiguran|free)\b",
    ],
    "paid_flight": [
        r"\b(flight|avionska karta|let)\b.*\b(paid|plaćen|covered)\b",
    ],
}


def extract_perks(description: str) -> dict:
    """Vrati dict sa bool vrijednostima za svaki perk."""
    t = (description or "").lower()
    return {
        k: any(re.search(p, t) for p in patterns)
        for k, patterns in PERKS.items()
    }