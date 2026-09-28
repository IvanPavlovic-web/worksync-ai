"""Centralna funkcija koja klasifikuje jedan RawJob → Job fields."""

from app.classifier.job_classifier import classify_job
from app.classifier.location_parser import classify_location, resolve_countries
from app.classifier.perks_parser import extract_perks
from app.classifier.visa_checker import detect_visa_sponsorship


def enrich_job(raw) -> dict:
    """
    Ulaz: RawJob (dataclass sa poljima source, external_id, title, company, url, description, location)
    Izlaz: dict spreman za Job(**dict).
    """
    title = raw.title or ""
    description = raw.description or ""
    location = raw.location or ""

    work_mode, countries, city = classify_location(location, description)
    allowed = resolve_countries(countries)
    perks = extract_perks(description)
    visa = detect_visa_sponsorship(description)
    cls = classify_job(title, description)

    country_code = None
    for c in countries:
        if c not in ("EU", "GLOBAL") and len(c) == 2:
            country_code = c
            break

    return {
        "source": raw.source,
        "external_id": raw.external_id,
        "title": title,
        "company": raw.company,
        "url": raw.url,
        "description": description,
        "location": location,
        "city": city,
        "country_code": country_code,
        "work_mode": work_mode,
        "allowed_countries": allowed,
        "visa_sponsorship": visa,
        "relocation_support": perks["relocation_support"],
        "housing_provided": perks["housing_provided"],
        "meal_provided": perks["meal_provided"],
        "salary_min": raw.salary_min,
        "salary_max": raw.salary_max,
        "currency": raw.currency,
        "posted_at": raw.posted_at,
        "language": cls["language"],
        "category": cls["category"],
        "seniority": cls["seniority"],
    }