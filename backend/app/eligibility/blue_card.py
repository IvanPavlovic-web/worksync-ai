"""Provjera EU Blue Card uslova."""


BLUE_CARD = {
    "DE": 43800,
    "DE_shortage": 41041,
    "AT": 45300,
    "NL": 67200,
    "FR": 53836,
    "SE": 57000,
    "IE": 64000,
    "LU": 58400,
}

# Zemlje gdje je Blue Card u DKK, NOK, CHF...
CURRENCY_RATES_TO_EUR = {
    "EUR": 1.0,
    "USD": 0.92,
    "GBP": 1.17,
    "CHF": 1.05,
    "BAM": 0.51,
    "RSD": 0.0085,
    "HRK": 0.133,   # samo povijesno
    "DKK": 0.134,
    "NOK": 0.086,
    "SEK": 0.088,
    "PLN": 0.23,
    "CZK": 0.040,
}


def to_eur(amount: float, currency: str) -> float:
    rate = CURRENCY_RATES_TO_EUR.get((currency or "EUR").upper(), 1.0)
    return amount * rate


def blue_card_ok(job) -> tuple[bool, str]:
    """
    Vraća (ok, reason).
    Pretpostavlja da je plata godišnja; ako je hourly/monthly, konvertuj.
    """
    countries = set(job.allowed_countries or [])
    target = None
    for c in countries:
        if c in BLUE_CARD:
            target = c
            break
    if not target:
        return False, "Blue Card nije primjenjiv (nije EU zemlja sa pragom)"

    salary = job.salary_max or job.salary_min
    if not salary:
        return False, "Nema podataka o plati"

    # Konverzija u godišnju ako treba
    period = (job.salary_period or "year").lower()
    if period == "hour":
        salary *= 2080
    elif period == "month":
        salary *= 12

    salary_eur = to_eur(float(salary), job.currency or "EUR")
    threshold = BLUE_CARD[target]

    # IT ima sniženi prag u DE
    if target == "DE" and job.category == "it":
        threshold = BLUE_CARD["DE_shortage"]

    if salary_eur >= threshold:
        return True, f"Blue Card OK ({salary_eur:.0f} EUR ≥ {threshold} EUR)"
    return False, f"Blue Card plata preniska ({salary_eur:.0f} < {threshold} EUR)"