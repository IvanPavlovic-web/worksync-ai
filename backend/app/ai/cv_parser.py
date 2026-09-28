import re
from datetime import datetime

SKILLS = r"python|javascript|typescript|java|c#|php|go|rust|sql|react|vue|angular|django|fastapi|node(?:\.js)?|docker|kubernetes|aws|azure|figma|excel|photoshop"
LANGUAGES = {"bosnian": "bs", "bosanski": "bs", "croatian": "hr", "hrvatski": "hr", "serbian": "sr", "srpski": "sr", "english": "en", "engleski": "en", "german": "de", "njemački": "de", "njemacki": "de"}

def parse_cv_text(text: str) -> dict:
    clean = re.sub(r"\s+", " ", text).strip()
    found = sorted({m.group(0).lower() for m in re.finditer(SKILLS, clean, re.I)})
    years = [int(x) for x in re.findall(r"(?:19|20)\d{2}", clean)]
    experience = max(0, datetime.now().year - min(years)) if years else 0
    seniority = "junior" if experience < 2 else "mid" if experience < 5 else "senior" if experience < 8 else "lead"
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", clean)
    languages = [{"code": code, "level": "B2"} for name, code in LANGUAGES.items() if name in clean.lower()]
    return {"primary_role": _role(clean), "years_experience": experience, "seniority": seniority, "top_skills": found, "soft_skills": [], "languages": languages, "preferred_timezone": None, "summary": clean[:500], "experiences": [], "skills": [{"name": s, "category": "Other", "level": seniority.title(), "years": None} for s in found], "education": [], "certifications": [], "preferred_locations": [], "willing_to_relocate": bool(re.search(r"relocat|selidb", clean, re.I)), "requires_visa_sponsorship": bool(re.search(r"visa|viza|sponsor", clean, re.I)), "email": email.group(0) if email else None, "_detected_language": "bs"}

def _role(text: str) -> str | None:
    match = re.search(r"(?:position|role|pozicija|titula)\s*[:\-]?\s*([^|,;]{3,80})", text, re.I)
    return match.group(1).strip() if match else None

def parse_date(value: str | None) -> datetime | None:
    if not value or value == "null": return None
    for fmt in ("%Y-%m", "%Y"):
        try: return datetime.strptime(value, fmt)
        except ValueError: pass
    return None
