import re

from langdetect import detect


SENIORITY_PATTERNS = {
    "intern": r"\b(intern|internship|praksa|praktikum|volonter)\b",
    "junior": r"\b(junior|jr\.?\b|entry[\s-]level|početnik|bez iskustva|graduate)\b",
    "mid": r"\b(mid[\s-]level|medior|middle|mid\b)\b",
    "senior": r"\b(senior|sr\.?\b|lead|principal|staff|ekspert|expert)\b",
    "lead": r"\b(team lead|tech lead|head of|direktor|manager|vp\b)\b",
}

CATEGORY_PATTERNS = {
    "it": r"\b(developer|engineer|programmer|software|devops|sre|data|ml|ai|fullstack|frontend|backend|qa)\b",
    "design": r"\b(designer|ux|ui|figma|grafik|illustrator)\b",
    "marketing": r"\b(marketing|seo|content|social media|copywriter|ppc|growth)\b",
    "sales": r"\b(sales|account manager|business development|prodaja|bdr|sdr)\b",
    "finance": r"\b(finance|accountant|računovođa|bookkeeper|controller)\b",
    "support": r"\b(customer support|help desk|call center|podrška|client support)\b",
    "hr": r"\b(hr\b|recruiter|talent|human resources|zapošljavanje)\b",
    "construction": r"\b(građevina|construction|baustelle|majstor|tesar|zidar|električar|vodoinstalater)\b",
    "healthcare": r"\b(nurse|doctor|medical|pflege|zdravstvo|medicinska|njegovatelj)\b",
    "hospitality": r"\b(waiter|chef|hotel|restaurant|konobar|kuvar|recepcija)\b",
    "logistics": r"\b(driver|warehouse|forklift|vozač|magacioner|lager|skladište)\b",
    "education": r"\b(teacher|professor|nastavnik|učitelj|tutor)\b",
    "legal": r"\b(lawyer|attorney|pravnik|advokat|paralegal)\b",
}


def classify_job(title: str, description: str) -> dict:
    text = f"{title}\n{description[:3000]}".lower()

    seniority = "mid"
    for level, pattern in SENIORITY_PATTERNS.items():
        if re.search(pattern, text):
            seniority = level
            break

    category = "other"
    for cat, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, text):
            category = cat
            break

    try:
        language = detect(f"{title} {description[:1500]}")
    except Exception:
        language = "en"

    return {
        "seniority": seniority,
        "category": category,
        "language": language,
    }