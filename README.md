# WorkSync AI

Job aggregation and candidate workflow application for Bosnia and Herzegovina, the wider Balkan region, EU relocation and remote work. The system pulls postings from regional job boards, EU relocation portals, remote-first boards and public ATS endpoints, classifies and normalizes them, computes a local semantic match against a candidate profile and supports a review-first application workflow.

The repository is designed for local-first operation:

- No OpenAI, Anthropic, Sentry or hosted analytics dependency.
- Local multilingual embeddings with `paraphrase-multilingual-MiniLM-L12-v2`.
- Rule-based CV parsing with optional spaCy NER.
- Jinja2 cover-letter templates, no external LLM.
- Database-backed blog templates.
- FastAPI backend, PostgreSQL, Redis, Celery and Meilisearch.
- Next.js frontend with TypeScript, Tailwind and next-themes.

> Status: the development stack and smoke-tested API paths are wired. The first embedding call downloads the local model and caches it under the Sentence Transformers cache directory. Scraper catalog entries without a concrete public endpoint return no jobs until an adapter endpoint is configured, which is intentional and avoids undefined selectors.

---

## Architecture and flow

```text
Browser
  |
  +--> Next.js :3000 (App Router, SSR + ISR)
          |
          +--> FastAPI :8000
                  |
                  +--> PostgreSQL :5432   (jobs, users, applications, blog, vault)
                  +--> Redis :6380        (Celery broker, rate limits, apply queue)
                  +--> Meilisearch :7700  (indexed job search)
                  +--> Celery worker      (scraping, embedding, blog, autopilot)
                  +--> Celery beat        (scheduled tasks)
                  +--> external job pages (HTTPS, robots.txt aware)

Backend worker pipeline
  |
  +--> BaseScraperV2 (httpx, retry, robots.txt, canonical URL, UA rotation)
  +--> classifier.pipeline (work mode, country, city, perks, visa)
  +--> embedder (Sentence Transformers, 384-dim, multilingual)
  +--> matching (cosine similarity + keyword overlap)
  +--> Meilisearch sync
```

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI 0.115 |
| ASGI server | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Database driver | psycopg 3 |
| Vector storage | pgvector (extension) |
| Migrations | Alembic |
| Validation | Pydantic v2, pydantic-settings |
| Authentication | JWT via python-jose, scrypt password hashing |
| Background jobs | Celery 5.4, Redis broker |
| Search | Meilisearch 1.10 (self-hosted) |
| Embeddings | Sentence Transformers (paraphrase-multilingual-MiniLM-L12-v2) |
| NER | spaCy `xx_ent_wiki_sm` |
| HTTP client | httpx |
| HTML parsing | BeautifulSoup4, lxml |
| RSS | feedparser |
| Browser automation | Playwright (Chromium) |
| CV parsing | pypdf, python-docx |
| Templates | Jinja2 |
| Sanitization | Bleach |
| Fuzzy matching | rapidfuzz |
| Rate limiting | slowapi |
| Frontend framework | Next.js 16 (App Router) |
| Frontend language | TypeScript |
| Styling | Tailwind CSS 4 |
| Data fetching | TanStack Query, Axios |
| i18n | next-intl |
| Theming | next-themes |
| Icons | Lucide React |
| Runtime | Python 3.12, Node.js 20 |
| Containers | Docker, Docker Compose |

---

## Features

- Multi-source job aggregation. Regional job boards, EU relocation portals, remote-first boards and ATS providers, unified into a single normalized `Job` record.
- BaseScraperV2 with timeouts, retry with exponential backoff, robots.txt caching, User-Agent rotation, canonical URL normalization, per-source delay, in-memory URL deduplication and refusal when robots.txt disallows a URL.
- Job classification. Work mode detection (remote, hybrid, onsite), country and city extraction, seniority, category, employment type, language, detected salary and perks such as visa sponsorship, housing, meals, relocation support and language courses.
- Job deduplication. Near-duplicate postings across sources are merged using fuzzy matching on title and company, with `source_ids` recording every origin.
- Local multilingual embeddings. Sentence Transformers model runs on CPU, no external API, no API key, no per-request cost.
- Semantic matching. Hybrid score combining cosine similarity between profile and job embeddings with keyword overlap. Used by the candidate feed.
- Eligibility engine. Determines whether a candidate from Bosnia and Herzegovina (or the wider Balkan region) can realistically apply to a given job, factoring in work mode, allowed countries, visa sponsorship and EU Blue Card salary thresholds.
- CV import. Upload a PDF, DOCX, TXT or Markdown CV. The rule-based parser extracts role, skills, languages, years of experience and seniority, then fills the profile and vault.
- Cover letter generation. Jinja2 templates produce a short, structured letter from the candidate profile and job record. No external LLM.
- Application workflow. Save, prefill, apply, interview, offer and rejected stages are tracked. Optional autopilot adapters populate ATS forms for Greenhouse, Lever, Ashby and Workable, stopping before submission for user review.
- Public API for the Next.js frontend. Faceted job search with filters for work mode, country, city, category, seniority, employment type, salary range, visa, housing, relocation and posted-within days.
- Background blog generator. Produces localized guide posts from database aggregates with no external AI call.
- SEO-ready. Dynamic sitemap, robots rules, `JobPosting`, `BreadcrumbList`, `Article` and `Organization` JSON-LD, canonical URLs and OG metadata.
- Localized UI. Bosnian, Croatian, Serbian, English and German message catalogs with a URL-based locale switch.
- Dark and light themes with `next-themes` and system preference detection.
- Role-based access is implicit. Public endpoints are read-only; authenticated endpoints are scoped to the requesting user.

---

## Project structure

```text
worksync-ai/
├── backend/
│   ├── app/
│   │   ├── ai/                    Local embeddings, CV parser, cover-letter templates
│   │   ├── api/                   FastAPI routers (auth, profile, jobs, ai, public, blog, applications, search)
│   │   ├── autopilot/             Playwright browser, queue and ATS adapters
│   │   │   └── adapters/          greenhouse, lever, ashby, workable, linkedin
│   │   ├── classifier/            Job classification, location, perks, visa
│   │   ├── eligibility/           Country rules and EU Blue Card thresholds
│   │   ├── models/                SQLAlchemy models
│   │   ├── schemas/               Pydantic schemas
│   │   ├── scrapers/
│   │   │   ├── ats/               ashby, greenhouse, lever, smartrecruiters, workable
│   │   │   ├── boards/            arbeitnow, himalayas, jobicy, remoteok, remotive, wwr
│   │   │   ├── regional/          eures, helloworld_rs, make_it_in_germany, mojposao_ba, posao_ba, posao_hr
│   │   │   ├── base.py            BaseScraperV2
│   │   │   ├── catalog.py         Adapter for catalog sources with a configured endpoint
│   │   │   └── registry.py        Source registry and priority tiers
│   │   ├── services/              Matching, Meilisearch integration, slugging
│   │   ├── vault/                 Field-mapping for application form autofill
│   │   ├── workers/               Celery app, tasks, scheduled blog generation
│   │   ├── config.py              Settings loaded from environment
│   │   ├── database.py            Engine, session factory, schema init
│   │   └── main.py                FastAPI application factory
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   └── Dockerfile.beat
├── frontend/
│   ├── app/                       Next.js App Router pages
│   │   ├── poslovi/               Job listing and job detail (with [slug])
│   │   ├── blog/                  Blog listing and post (with [slug])
│   │   ├── dashboard/             Candidate feed
│   │   ├── profil/                Profile and vault editor
│   │   ├── kanban/                Application tracker
│   │   ├── login/                 Login
│   │   ├── register/              Registration
│   │   ├── sitemap.ts             Dynamic sitemap
│   │   └── robots.ts              Robots rules
│   ├── components/                UI primitives, filters, theme, auth gate
│   ├── lib/                       API client, auth handling, class names
│   ├── messages/                  bs, hr, sr, en, de message catalogs
│   ├── i18n.ts                    Locale configuration
│   ├── middleware.ts              Locale middleware
│   ├── next.config.mjs
│   ├── package.json
│   └── Dockerfile
├── scripts/
│   ├── setup.sh / setup.ps1       Bootstrap the local stack
│   ├── start.sh / start.ps1       Start infrastructure and application processes
│   ├── stop.sh / stop.ps1         Stop application processes and containers
│   ├── reset.sh / reset.ps1       Remove volumes and re-bootstrap
│   ├── seed.sh / seed.ps1         Prepare the database schema
│   ├── scrape.sh / scrape.ps1     Trigger a scrape tier
│   ├── reembed.sh / reembed.ps1   Re-embed all jobs
│   ├── doctor.sh / doctor.ps1     Verify the environment
│   └── logs.sh / logs.ps1         Tail container logs
├── docker-compose.yml             Local PostgreSQL, Redis and Meilisearch
├── docker-compose.prod.yml        Production topology (api, worker, beat, web, caddy)
├── Caddyfile                      Production reverse proxy and TLS
├── deploy.sh                      Production deploy helper
├── start-worksync.bat             Windows one-click launcher
└── README.md
```

---

## Setup

### Prerequisites

- Docker Desktop on Windows or macOS, or Docker Engine with Compose v2 on Linux.
- Python 3.12.
- Node.js 20 or newer.
- Git.

The setup scripts verify these tools and stop with a clear message if any are missing.

### Clone and bootstrap

Windows PowerShell:

```powershell
git clone https://github.com/IvanPavlovic-web/worksync-ai.git
cd worksync-ai
.\scripts\setup.ps1
.\start-worksync.bat
```

Linux and macOS:

```bash
git clone https://github.com/IvanPavlovic-web/worksync-ai.git
cd worksync-ai
./scripts/setup.sh
./scripts/start.sh
```

### What setup does

1. Verifies Python, Node.js and Docker are installed and reports versions.
2. Creates `.venv` at the repository root.
3. Installs backend dependencies from `backend/requirements.txt`.
4. Installs the Chromium browser used by Playwright.
5. Downloads the spaCy `xx_ent_wiki_sm` model for CV parsing.
6. Copies `backend/.env.example` to `backend/.env` if missing.
7. Copies `frontend/.env.example` to `frontend/.env.local` if missing.
8. Starts PostgreSQL, Redis and Meilisearch with Docker Compose.
9. Installs frontend dependencies with `npm ci`.

No API key is required for the local stack.

### What start does

- Ensures the Docker infrastructure is running.
- Opens separate process windows (or background processes on Linux and macOS) for:
  - FastAPI backend on `http://localhost:8000`
  - Celery worker on the `default` queue
  - Celery beat for scheduled tasks
  - Next.js frontend on `http://localhost:3000`

The Windows launcher is `start-worksync.bat`. It starts Docker infrastructure and calls `scripts/start.ps1`, which opens the four application processes in separate PowerShell windows.

### Access

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend health | http://localhost:8000/health |
| OpenAPI documentation | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6380 |
| Meilisearch | http://localhost:7700 |

### Database schema

Tables are created by the FastAPI startup hook and by the seed command after importing the model package. This is intentionally lightweight for local development.

```powershell
.\scripts\seed.ps1
```

```bash
./scripts/seed.sh
```

For production, add and run Alembic migrations before relying on `create_all` as a deployment mechanism. PostgreSQL is required for the supported development stack.

### Reset

```powershell
.\scripts\reset.ps1
```

```bash
./scripts/reset.sh
```

This removes Docker volumes for PostgreSQL, Redis and Meilisearch and re-runs setup. It is destructive for local data.

---

## Configuration

Copy the example files before changing values:

```powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env.local
```

### Backend

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://worksync:worksync@localhost:5432/worksync` | SQLAlchemy connection string |
| `REDIS_URL` | `redis://localhost:6380/0` | Celery broker and backend |
| `MEILI_URL` | `http://localhost:7700` | Meilisearch base URL |
| `MEILI_KEY` | empty | Optional Meilisearch API key |
| `JWT_SECRET` | placeholder | Replace with at least 16 random characters for any shared environment |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_MINUTES` | `60` | Access token lifetime |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated browser origins |
| `EMBEDDING_MODEL` | `paraphrase-multilingual-MiniLM-L12-v2` | Local Sentence Transformers model |
| `SITE_URL` | `http://localhost:3000` | Canonical site URL |

### Frontend

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api` | Browser API base URL |
| `API_URL` | `http://localhost:8000/api` | Server-side Next.js API base URL |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:3000` | Canonical URL and SEO metadata |

Never commit `.env`, `.env.local` or `*.env.prod`. Use a deployment secret manager or host-only files for production values.

---

## API reference

All endpoints are prefixed with `/api/`. Authenticated endpoints require a valid JWT access token in the `Authorization: Bearer <token>` header.

### Public (no authentication)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/api/public/jobs/latest` | Most recently scraped active jobs |
| GET | `/api/public/jobs/search` | Faceted search with filters and pagination |
| GET | `/api/public/jobs/by-filter` | Simple filter variant used by landing sections |
| GET | `/api/public/jobs/by-country` | Jobs filtered by ISO country code |
| GET | `/api/public/jobs/sitemap` | Slug list for the sitemap |
| GET | `/api/public/jobs/{slug}` | Job detail by slug |
| GET | `/api/public/cities` | Cities with job counts |
| GET | `/api/public/categories` | Categories with job counts |
| GET | `/api/public/countries` | Countries with job counts |
| GET | `/api/public/stats` | Aggregate counts (total, remote, visa, housing) |
| GET | `/api/blog` | Blog listing |
| GET | `/api/blog/{slug}` | Blog post detail |
| GET | `/api/search` | Meilisearch keyword search |

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account, returns JWT |
| POST | `/api/auth/login` | Obtain JWT |

### Authenticated

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/profile` | Current user profile and skills |
| POST | `/api/ai/import-cv` | Upload CV, parse, and populate the profile |
| POST | `/api/ai/cover-letter/{job_id}` | Generate a cover letter from profile and job |
| GET | `/api/jobs/feed` | Semantic match feed for the current user |
| GET | `/api/jobs/{job_id}` | Job detail for authenticated views |
| GET | `/api/applications` | List tracked applications |
| POST | `/api/applications` | Save a job to the tracker |
| PATCH | `/api/applications/{app_id}` | Update application status |
| DELETE | `/api/applications/{app_id}` | Remove a tracked application |
| POST | `/api/applications/auto-apply/{job_id}` | Enqueue an autopilot apply task |
| POST | `/api/applications/auto-apply-bulk` | Enqueue a batch of autopilot apply tasks |

Interactive documentation is available at `http://localhost:8000/docs`.

### Faceted search

`GET /api/public/jobs/search` accepts:

- `work_mode`
- `seniority`
- `category`
- `country`
- `city`
- `employment_type`
- `salary_min`
- `salary_max`
- `posted_within`
- `visa_only`
- `housing_only`
- `relocation_only`
- `language`
- `source`
- `query`
- `sort` with values `newest`, `salary`, `relevance`, `match_score`
- `limit`
- `offset`

The response contains `total`, `items`, `facets` and `next_offset`.

Example:

```text
GET /api/public/jobs/search?query=python&work_mode=remote&country=DE&salary_min=40000&sort=salary
```

The frontend synchronizes search state with the URL and provides an instant query field, a filter sidebar and a clear-filter action.

---

## Scrapers

Concrete adapters cover remote boards, EURES, selected regional sources and ATS providers.

### Remote boards

- Remotive
- Jobicy
- We Work Remotely (RSS across multiple categories)
- RemoteOK
- Arbeitnow
- Himalayas

### Regional and relocation

- Posao.ba
- MojPosao.ba
- Posao.hr
- HelloWorld.rs
- EURES (official EU mobility API)
- Make it in Germany

### ATS providers

- Greenhouse (public job board API)
- Lever (public postings API)
- Ashby (public GraphQL job board)
- Workable (public widget API)
- SmartRecruiters (public postings API)

### BaseScraperV2

All adapters inherit from `BaseScraperV2`, which provides:

- Timeouts at request and connection level.
- Retry with exponential backoff.
- robots.txt caching per host, with a fail-open default when the file cannot be read.
- User-Agent rotation across a small pool of realistic clients.
- Canonical URL normalization (lowercased scheme and host, trailing slash trimmed).
- Per-source delay with jitter.
- In-memory URL deduplication before persisting.
- Refusal to fetch URLs disallowed by robots.txt.

### Catalog sources

The registry also contains named catalog entries for sources that do not expose a stable public JSON or RSS endpoint. These entries deliberately return no jobs until a concrete endpoint or dedicated parser is configured. This avoids fake integrations, undefined selectors and accidental scraping of unsupported pages.

Run a manual scrape:

```powershell
.\scripts\scrape.ps1
```

```bash
./scripts/scrape.sh
```

---

## Background jobs

Celery tasks include:

- Scraping by tier (`critical`, `high`, `medium`) or by single source.
- Embedding new jobs and profiles.
- Re-embedding all jobs after a model change.
- Synchronizing the Meilisearch index.
- Deactivating jobs older than a configurable window.
- Processing the autopilot apply queue.
- Generating localized blog posts from database aggregates.

The Celery beat schedule ships with scrape tiers, embedding, Meilisearch sync, old-job deactivation and a daily blog batch.

Start worker and beat separately when needed:

```powershell
celery -A app.workers.celery_app.celery worker -l info --pool=solo  # Windows
celery -A app.workers.celery_app.celery beat -l info
```

Re-embed jobs:

```powershell
.\scripts\reembed.ps1
```

The first embedding call downloads the configured local model and caches it in the standard Sentence Transformers directory. Subsequent calls reuse the cache.

---

## Tests and verification

Current repository verification commands:

```powershell
$env:PYTHONPATH = "backend"
python -m compileall -q backend/app
python -c "from sqlalchemy.orm import configure_mappers; from app.main import app; configure_mappers(); print('backend ok')"

cd frontend
npm ci
npm run lint
npm run build
```

The API smoke paths verified during the audit are:

- `GET /health`
- Database schema initialization
- Registration
- Login
- Public faceted job search

There is currently no committed pytest suite. A proper test suite should be the next engineering task, with isolated PostgreSQL fixtures and scraper response fixtures.

---

## Troubleshooting

### Docker is not running

Start Docker Desktop, then check:

```powershell
docker info
docker compose ps
```

### Backend says a relation does not exist

Run:

```powershell
.\scripts\seed.ps1
```

Make sure `backend/.env` points to the same PostgreSQL instance used by Docker.

### Frontend loads but API requests fail

Check both values in `frontend/.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000/api
API_URL=http://localhost:8000/api
```

Restart the Next.js process after changing env files.

### Redis or Celery cannot connect

The host port is 6380 while the container port is 6379:

```powershell
docker compose ps
docker compose logs redis
```

### A port is already in use

Find the process:

```powershell
Get-NetTCPConnection -LocalPort 3000,8000,5432,6380,7700 -ErrorAction SilentlyContinue
```

Stop the old process or change the port mapping in Compose and the matching env value.

### A scraper returns no jobs

Check:

- robots.txt permission.
- Source response status.
- Parser selectors or JSON shape.
- Retry logs.
- Source registry configuration.
- Whether the catalog source has a configured endpoint.

Do not bypass robots.txt or add credentials to make a scraper work.

### Embedding is slow the first time

This is expected on the first local model load. The model is cached after the first successful call. Use reembed only after changing the model or the embedding input text.

### Inspect logs

```powershell
.\scripts\logs.ps1
docker compose logs -f postgres redis meilisearch
```

---

## Deployment notes

The production files are:

- `docker-compose.prod.yml`
- `backend/Dockerfile`
- `backend/Dockerfile.worker`
- `backend/Dockerfile.beat`
- `frontend/Dockerfile`
- `Caddyfile`
- `deploy.sh`

Before deployment:

1. Create real host-only env files for backend, frontend and the Compose stack.
2. Replace `JWT_SECRET` with at least 32 random characters.
3. Use a non-default PostgreSQL password.
4. Configure production CORS origins.
5. Put the application behind HTTPS (Caddy in the shipped Compose file).
6. Run migrations.
7. Back up PostgreSQL and the Docker volumes.
8. Configure logs and restart policy.
9. Validate `/health` after deploy.

Do not put passwords, JWT secrets or third-party credentials in GitHub.

---

## Security boundaries

- Passwords are hashed with Python scrypt and per-user salts.
- JWT tokens carry an expiry and are validated on every authenticated request.
- CORS is allowlist-based and read from `CORS_ORIGINS`.
- Public job and blog HTML is sanitized with Bleach before being returned.
- Scrapers normalize URLs and respect robots.txt.
- Scraper requests use timeouts and retries.
- Search filters use SQLAlchemy expressions rather than string-built SQL.
- Local `.env` and production env files are ignored by Git.

Autopilot application adapters should only be used with explicit user intent and should be tested against each ATS independently. The default configuration stops before submission so the candidate can review every application.

---

## Contributing

Before opening a pull request:

```powershell
python -m compileall -q backend/app
cd frontend
npm run lint
npm run build
```

Please include:

- What changed.
- Why it changed.
- How it was tested.
- Migration or env changes.
- Screenshots for UI changes.
- Scraper fixtures for parser changes.
- Rollback notes for production-impacting changes.

---

## License

Proprietary. Copyright (c) WorkSync AI contributors. All rights reserved. Redistribution or commercial use without prior written permission is prohibited.
