from jinja2 import BaseLoader, Environment
from app.models import Job, Profile

TEMPLATES = {
    "bs": "Poštovani,\n\nPrijavljujem se za poziciju {{ job.title }} u kompaniji {{ job.company }}. Moje iskustvo u oblastima {{ skills }} odgovara zahtjevima oglasa.\n\nKao {{ profile.title or 'stručnjak' }}, mogu doprinijeti praktičnim radom, jasnom komunikacijom i odgovornošću. {{ profile.summary or 'Rado ću detaljnije predstaviti svoje iskustvo.' }}\n\nSrdačan pozdrav,\n{{ name }}",
    "en": "Dear Hiring Team,\n\nI am applying for the {{ job.title }} role at {{ job.company }}. My experience with {{ skills }} matches the position.\n\nAs {{ profile.title or 'a professional' }}, I can contribute through practical delivery, clear communication, and ownership. {{ profile.summary or 'I would welcome an interview.' }}\n\nKind regards,\n{{ name }}",
}

def generate_cover_letter(profile: Profile, job: Job, language: str = "bs") -> str:
    template = Environment(loader=BaseLoader(), autoescape=False).from_string(TEMPLATES.get(language, TEMPLATES["bs"]))
    return template.render(job=job, profile=profile, skills=", ".join(s.name for s in profile.skills or []) or "relevant skills", name=getattr(profile.user, "full_name", None) or "Kandidat")
