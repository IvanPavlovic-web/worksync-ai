import re
from typing import Tuple


REMOTE_KW = [
    r"\bremote\b", r"\bfully[\s-]remote\b", r"\b100%\s*remote\b",
    r"\bwork[\s-]from[\s-]anywhere\b", r"\bwfa\b", r"\bremote[\s-]first\b",
    r"\banywhere\b", r"\bdistributed[\s-]team\b", r"\bremote[\s-]friendly\b",
    r"\bhome[\s-]?office\b", r"\brad od kuće\b", r"\bremote rad\b",
]
HYBRID_KW = [
    r"\bhybrid\b", r"\b\d+\s*days?\s*(in|per)\s*(office|week)\b",
    r"\bflexible[\s-]office\b", r"\bhibridno\b",
]
ONSITE_KW = [
    r"\bon[\s-]?site\b", r"\bin[\s-]?office\b", r"\boffice[\s-]based\b",
    r"\bu kancelariji\b", r"\bna licu mjesta\b",
]


COUNTRY_PATTERNS = {
    "US": [r"\bunited[\s-]states\b", r"\busa\b", r"\bu\.s\.", r"\bus[\s-]?only\b", r"\bus[\s-]?based\b"],
    "CA": [r"\bcanada\b", r"\bcanadian\b"],
    "GB": [r"\buk\b", r"\bunited[\s-]kingdom\b", r"\bbritain\b", r"\bengland\b", r"\bscotland\b"],
    "DE": [r"\bgermany\b", r"\bdeutschland\b", r"\bberlin\b", r"\bmunich\b", r"\bmünchen\b", r"\bhamburg\b"],
    "NL": [r"\bnetherlands\b", r"\bamsterdam\b", r"\brotterdam\b", r"\bholland\b"],
    "FR": [r"\bfrance\b", r"\bparis\b", r"\blyon\b"],
    "ES": [r"\bspain\b", r"\bmadrid\b", r"\bbarcelona\b", r"\bvalencia\b"],
    "IT": [r"\bitaly\b", r"\bmilan\b", r"\brome\b", r"\bturin\b"],
    "PL": [r"\bpoland\b", r"\bwarsaw\b", r"\bkrakow\b", r"\bwroclaw\b"],
    "RS": [r"\bserbia\b", r"\bbelgrade\b", r"\bnovi sad\b", r"\bsrbija\b", r"\bbeograd\b"],
    "HR": [r"\bcroatia\b", r"\bzagreb\b", r"\bsplit\b", r"\bhrvatska\b"],
    "BA": [r"\bbosnia\b", r"\bsarajevo\b", r"\bbanja luka\b", r"\bbosna\b", r"\bhercegovina\b", r"\btuzla\b", r"\bmostar\b"],
    "SI": [r"\bslovenia\b", r"\bljubljana\b", r"\bslovenija\b"],
    "MK": [r"\bmacedonia\b", r"\bskopje\b", r"\bmakedonija\b"],
    "ME": [r"\bmontenegro\b", r"\bpodgorica\b", r"\bcrna gora\b"],
    "BG": [r"\bbulgaria\b", r"\bsofia\b"],
    "RO": [r"\bromania\b", r"\bbucharest\b", r"\bbucuresti\b"],
    "HU": [r"\bhungary\b", r"\bbudapest\b"],
    "CZ": [r"\bczech\b", r"\bprague\b", r"\bpraha\b"],
    "SK": [r"\bslovakia\b", r"\bbratislava\b"],
    "PT": [r"\bportugal\b", r"\blisbon\b", r"\blisboa\b", r"\bporto\b"],
    "CH": [r"\bswitzerland\b", r"\bzurich\b", r"\bzürich\b", r"\bgeneva\b"],
    "AT": [r"\baustria\b", r"\bvienna\b", r"\bwien\b"],
    "SE": [r"\bsweden\b", r"\bstockholm\b"],
    "NO": [r"\bnorway\b", r"\boslo\b"],
    "DK": [r"\bdenmark\b", r"\bcopenhagen\b", r"\bkbh\b"],
    "FI": [r"\bfinland\b", r"\bhelsinki\b"],
    "IE": [r"\bireland\b", r"\bdublin\b"],
    "AU": [r"\baustralia\b", r"\bsydney\b", r"\bmelbourne\b"],
    "NZ": [r"\bnew zealand\b", r"\bauckland\b", r"\bwellington\b"],
    "IN": [r"\bindia\b", r"\bbangalore\b", r"\bhyderabad\b", r"\bmumbai\b"],
    "BR": [r"\bbrazil\b", r"\bs[ãa]o paulo\b", r"\brio\b"],
    "UA": [r"\bukraine\b", r"\bkyiv\b", r"\bкиїв\b"],
    "TR": [r"\bturkey\b", r"\btürkiye\b", r"\bistanbul\b", r"\bankara\b"],
}

EU_COUNTRIES = {
    "DE", "NL", "FR", "ES", "IT", "PL", "PT", "IE", "SE", "DK", "FI",
    "AT", "BE", "LU", "CZ", "SK", "HU", "RO", "BG", "HR", "SI", "GR",
    "EE", "LV", "LT", "MT", "CY",
}


def classify_location(location: str, description: str = "") -> Tuple[str, list[str], str | None]:
    """
    Vraća: (work_mode, allowed_countries, city)
      work_mode: 'remote' | 'hybrid' | 'onsite'
      allowed_countries: lista ISO kodova, plus 'GLOBAL' ili 'EU'
      city: naziv grada (best-effort)
    """
    text = f"{location}\n{description[:4000]}".lower()

    # Odredi mod
    has_remote = any(re.search(p, text) for p in REMOTE_KW)
    has_hybrid = any(re.search(p, text) for p in HYBRID_KW)
    has_onsite = any(re.search(p, text) for p in ONSITE_KW)

    if has_hybrid:
        mode = "hybrid"
    elif has_remote and not (has_onsite and not has_remote):
        mode = "remote"
    elif has_onsite:
        mode = "onsite"
    else:
        mode = "onsite"

    # Detektuj zemlje
    countries = []
    for code, patterns in COUNTRY_PATTERNS.items():
        if any(re.search(p, text) for p in patterns):
            countries.append(code)

    # Regioni
    if re.search(r"\b(eu|europe|emea|eea|european union)\b", text):
        countries.append("EU")
    if re.search(r"\bworldwide\b|\banywhere\b|\bglobal\b|\bwork from anywhere\b", text):
        countries.append("GLOBAL")

    if not countries:
        countries = ["GLOBAL"] if mode == "remote" else []

    # Grad (best-effort)
    city = None
    if location:
        m = re.match(r"^([^,\(]+)", location.strip())
        if m:
            city = m.group(1).strip()

    return mode, list(dict.fromkeys(countries)), city


def resolve_countries(codes: list[str]) -> list[str]:
    """EU → lista zemalja, GLOBAL ostaje wildcard."""
    if "GLOBAL" in codes:
        return ["GLOBAL"]
    out = set()
    for c in codes:
        if c == "EU":
            out.update(EU_COUNTRIES)
        else:
            out.add(c)
    return sorted(out)