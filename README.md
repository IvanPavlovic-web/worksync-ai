# WorkSync

WorkSync je lokalno pokrenuta platforma za pretragu poslova, profile kandidata i prijave. Aplikacija ne zavisi od plaćenih AI, analytics ili error-tracking servisa.

## Arhitektura

- Backend: FastAPI, SQLAlchemy 2, PostgreSQL + pgvector image, Redis i Celery
- Lokalna obrada: `paraphrase-multilingual-MiniLM-L12-v2`, regex CV parser, Jinja2 template-i
- Search: SQL filteri, cosine similarity i keyword overlap
- Frontend: Next.js, TypeScript, Tailwind, Lucide i `next-themes`

## Pokretanje

Linux/macOS:

```bash
./scripts/setup.sh
./scripts/start.sh
```

Windows PowerShell:

```powershell
.\scripts\setup.ps1
.\scripts\start.ps1
```

Korisne skripte imaju Bash i PowerShell varijantu: `stop`, `reset`, `seed`, `scrape`, `reembed`, `doctor` i `logs`. Konfiguracija se kopira iz `backend/.env.example`. Placeholder tajne treba zamijeniti lokalnim vrijednostima; nijedan API ključ nije potreban.

## Search API

`GET /api/public/jobs/search` podržava `work_mode`, `seniority`, `category`, `country`, `city`, `employment_type`, `salary_min`, `salary_max`, `posted_within`, `visa_only`, `housing_only`, `relocation_only`, `language`, `source`, `query`, `sort`, `limit` i `offset`. Odgovor uključuje `facets` i `next_offset`.

## Scraping

Postojeći adapteri koriste robots.txt cache, timeout, retry, rotaciju User-Agent-a, canonical URL deduplication i rate delay. Izvori bez stabilnog adaptera nalaze se u katalogu i aktiviraju se dodavanjem javnog JSON endpointa u registry, bez lažnih URL-ova ili ključeva.
