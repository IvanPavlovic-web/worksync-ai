"""Pravila: može li korisnik iz države X aplicirati za posao Y."""


EU = {
    "DE", "NL", "FR", "ES", "IT", "PL", "PT", "IE", "SE", "DK", "FI",
    "AT", "CH", "BE", "LU", "CZ", "SK", "HU", "RO", "BG", "HR", "SI",
    "GR", "EE", "LV", "LT", "MT", "CY",
}

NON_EU_BALKAN = {"BA", "RS", "MK", "ME", "AL", "XK"}

# Western Balkans shema — ubrzana radna dozvola u DE
WB_SCHEME_COUNTRIES = {"DE"}

# EU Blue Card pragovi (godišnja bruto plata u EUR)
BLUE_CARD = {
    "DE": 43800,
    "DE_shortage": 41041,   # IT, medicine, engineering
    "AT": 45300,
    "NL": 67200,
    "FR": 53836,
    "SE": 57000,
    "IE": 64000,
    "DK": 514000,           # DKK ≈ 69.000 EUR — konverzija se radi u blue_card.py
    "LU": 58400,
}


def can_apply(job, profile) -> dict:
    """
    Vraća:
      {
        "eligible": bool,
        "reason": str,
        "score_penalty": float (0.0 = idealno, 1.0 = nikako),
        "notes": [str]
      }
    """
    user_country = (getattr(profile, "location_country", None) or "").upper()
    job_countries = set(job.allowed_countries or [])
    notes: list[str] = []
    penalty = 0.0

    if not user_country:
        return {
            "eligible": True,
            "reason": "Nepoznata tvoja država",
            "score_penalty": 0.1,
            "notes": ["Popuni svoju državu u profilu za tačniji match"],
        }

    # 1) GLOBAL remote
    if "GLOBAL" in job_countries and job.work_mode == "remote":
        return {
            "eligible": True,
            "reason": "Worldwide remote — možeš raditi iz svoje zemlje",
            "score_penalty": 0.0,
            "notes": [],
        }

    # 2) Remote sa restrikcijama
    if job.work_mode == "remote":
        if user_country in job_countries:
            return {
                "eligible": True,
                "reason": f"Remote u tvojoj državi ({user_country})",
                "score_penalty": 0.0,
                "notes": [],
            }

        if user_country in EU and any(c in EU for c in job_countries):
            return {
                "eligible": True,
                "reason": "EU remote — pokriveno tvojom EU državljanstvom",
                "score_penalty": 0.05,
                "notes": [],
            }

        if user_country in NON_EU_BALKAN:
            if "EU" in job_countries or any(c in EU for c in job_countries):
                penalty += 0.15
                notes.append("EU remote — možeš raditi samo kao B2B/freelancer iz BiH")
                return {
                    "eligible": True,
                    "reason": "EU remote (B2B potreban)",
                    "score_penalty": penalty,
                    "notes": notes,
                }
            return {
                "eligible": False,
                "reason": f"Posao traži {sorted(job_countries) or 'određenu državu'}, ti si {user_country}",
                "score_penalty": 1.0,
                "notes": notes,
            }

        return {
            "eligible": False,
            "reason": f"Nisi u dozvoljenim državama: {sorted(job_countries)}",
            "score_penalty": 1.0,
            "notes": notes,
        }

    # 3) Hybrid / Onsite
    if job.work_mode in ("hybrid", "onsite"):
        if user_country in job_countries:
            return {
                "eligible": True,
                "reason": "Lokalno u tvojoj državi",
                "score_penalty": 0.0,
                "notes": [],
            }

        if job.visa_sponsorship and user_country in NON_EU_BALKAN:
            for country in job_countries:
                if country in WB_SCHEME_COUNTRIES:
                    return {
                        "eligible": True,
                        "reason": f"{country} — Western Balkans shema (brža radna dozvola)",
                        "score_penalty": penalty + 0.15,
                        "notes": notes + ["Potrebna viza + relocation"],
                    }
            return {
                "eligible": True,
                "reason": "Visa sponsorship osiguran",
                "score_penalty": penalty + 0.25,
                "notes": notes + ["Potrebna viza i selidba"],
            }

        if job.relocation_support and user_country in NON_EU_BALKAN:
            return {
                "eligible": True,
                "reason": "Relocation support (provjeri vizu)",
                "score_penalty": penalty + 0.35,
                "notes": notes + ["Provjeri uslove za radnu dozvolu"],
            }

        return {
            "eligible": False,
            "reason": "On-site bez vize — ne možeš aplicirati iz svoje zemlje",
            "score_penalty": 1.0,
            "notes": notes,
        }

    return {
        "eligible": True,
        "reason": "Nepoznato — provjeri ručno",
        "score_penalty": 0.1,
        "notes": notes,
    }