# WorkSync AI

WorkSync AI is a job aggregation and candidate workflow application for Bosnia and Herzegovina, the region, EU relocation and remote work.

The repository is designed for local-first operation:

- no OpenAI, Anthropic, Sentry or hosted analytics dependency
- local multilingual embeddings with paraphrase-multilingual-MiniLM-L12-v2
- rule-based CV parsing
- Jinja2 cover-letter templates
- database-backed blog templates
- FastAPI backend, PostgreSQL, Redis, Celery and Meilisearch
- Next.js frontend with TypeScript and next-themes

> Status: the development stack and smoke-tested API paths are wired. The first embedding run downloads the local model. Scraper catalog entries without a concrete public endpoint intentionally return no jobs until an adapter endpoint is configured.

## Quick start

### Windows

Install Docker Desktop, Python 3.12+ and Node.js 20+.

~~~powershell
git clone https://github.com/IvanPavlovic-web/worksync-ai.git
cd worksync-ai
.\scripts\setup.ps1
.\start-worksync.bat
~~~

### Linux/macOS

Install Docker, Python 3.12+ and Node.js 20+.

~~~bash
git clone https://github.com/IvanPavlovic-web/worksync-ai.git
cd worksync-ai
./scripts/setup.sh
./scripts/start.sh
~~~

Open:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health
- OpenAPI docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6380
- Meilisearch: http://localhost:7700

The Windows launcher is [start-worksync.bat](./start-worksync.bat). It starts Docker infrastructure and opens separate windows for the backend, Celery worker, Celery beat and frontend.

## What setup does

The setup scripts:

1. check Python, Node.js and Docker
2. create .venv
3. install backend dependencies
4. install the Chromium browser used by Playwright
5. install frontend dependencies with npm ci
6. create backend/.env from backend/.env.example
7. create frontend/.env.local from frontend/.env.example
8. start PostgreSQL, Redis and Meilisearch

No API key is required for the local stack.

## Repository layout

~~~text
backend/
  app/
    ai/              local embeddings, CV parser, Jinja templates
    api/             FastAPI routers and auth dependencies
    classifier/      job classification and location/perks extraction
    models/          SQLAlchemy models
    scrapers/        source adapters and BaseScraperV2
    services/        matching and search integration
    workers/         Celery worker tasks and scheduled jobs
  .env.example
  requirements.txt
frontend/
  app/               Next.js App Router pages
  components/        UI primitives and job filters
  lib/               API client and token handling
  messages/          locale files
scripts/
  setup, start, stop, reset, seed, scrape, reembed, doctor, logs
docker-compose.yml   local PostgreSQL, Redis and Meilisearch
start-worksync.bat   Windows one-click launcher
~~~

## Runtime architecture

~~~text
Browser
  |
  +--> Next.js :3000
          |
          +--> FastAPI :8000
                  |
                  +--> PostgreSQL :5432
                  +--> Redis :6380
                  +--> Meilisearch :7700
                  +--> Celery worker / beat
                  +--> external public job pages
~~~

Development runs the application processes on the host for fast reload. Docker Compose runs the stateful services. The backend and frontend Dockerfiles are available for image builds, but the default developer path uses the host processes started by the scripts.

## Configuration

Copy the examples before changing values:

~~~powershell
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env.local
~~~

| Variable | Default | Purpose |
|---|---|---|
| DATABASE_URL | local PostgreSQL URL | SQLAlchemy database connection |
| REDIS_URL | redis://localhost:6380/0 | Celery broker/backend |
| MEILI_URL | http://localhost:7700 | self-hosted search |
| MEILI_KEY | empty | optional local Meilisearch key |
| JWT_SECRET | placeholder | replace for any shared environment |
| CORS_ORIGINS | http://localhost:3000 | comma-separated browser origins |
| EMBEDDING_MODEL | paraphrase-multilingual-MiniLM-L12-v2 | local Sentence Transformers model |
| NEXT_PUBLIC_API_URL | http://localhost:8000/api | browser API base URL |
| API_URL | http://localhost:8000/api | server-side Next.js API base URL |
| NEXT_PUBLIC_SITE_URL | http://localhost:3000 | canonical URL and SEO metadata |

Never commit .env, .env.local or *.env.prod. Use a deployment secret manager or host-only files for production values.

## Database

Tables are created by the FastAPI startup hook and by the seed command after importing the model package. Current local initialization is intentionally lightweight:

~~~powershell
.\scripts\seed.ps1
~~~

~~~bash
./scripts/seed.sh
~~~

For production, add and run Alembic migrations before using create_all as a deployment mechanism. PostgreSQL is required for the supported development stack.

Reset all local state, including Docker volumes:

~~~powershell
.\scripts\reset.ps1
~~~

~~~bash
./scripts/reset.sh
~~~

This is destructive for local PostgreSQL, Redis and Meilisearch data.

## API surface

Public:

- GET /health
- GET /api/public/jobs/latest
- GET /api/public/jobs/search
- GET /api/public/jobs/{slug}
- GET /api/public/jobs/sitemap
- GET /api/public/cities
- GET /api/public/categories
- GET /api/public/countries
- GET /api/public/stats
- GET /api/blog
- GET /api/blog/{slug}

Authentication:

- POST /api/auth/register
- POST /api/auth/login

Authenticated:

- GET /api/profile
- POST /api/ai/import-cv
- POST /api/ai/cover-letter/{job_id}
- GET /api/jobs/feed
- GET /api/jobs/{job_id}
- GET /api/applications
- POST /api/applications
- PATCH /api/applications/{app_id}
- DELETE /api/applications/{app_id}

Interactive documentation is available at http://localhost:8000/docs.

## Job search

GET /api/public/jobs/search supports:

- work_mode
- seniority
- category
- country
- city
- employment_type
- salary_min
- salary_max
- posted_within
- visa_only
- housing_only
- relocation_only
- language
- source
- query
- sort=newest|salary|relevance|match_score
- limit
- offset

The response contains total, items, facets and next_offset.

Example:

~~~text
GET /api/public/jobs/search?query=python&work_mode=remote&country=DE&salary_min=40000&sort=salary
~~~

The frontend synchronizes search state with the URL and provides an instant query field, filter sidebar and clear-filter action.

## Scraping

Existing concrete adapters cover remote boards, EURES, selected regional sources and ATS providers.

BaseScraperV2 provides:

- timeout and connection timeout
- retry with backoff
- robots.txt caching
- User-Agent rotation
- canonical URL normalization
- per-source delay
- in-memory URL deduplication
- refusal when robots.txt disallows a URL

Run a manual scrape:

~~~powershell
.\scripts\scrape.ps1
~~~

~~~bash
./scripts/scrape.sh
~~~

The registry also contains named catalog entries for the requested sources. A catalog entry is deliberately disabled until a stable public JSON/RSS endpoint or a dedicated parser is configured. This avoids fake integrations, undefined selectors and accidental scraping of unsupported pages.

## Background jobs

Celery tasks include:

- scraping by tier or source
- embedding missing jobs
- re-embedding jobs
- Meilisearch synchronization
- old-job deactivation
- application queue processing
- database-backed blog generation

Start worker and beat separately when needed:

~~~powershell
celery -A app.workers.celery_app.celery worker -l info
celery -A app.workers.celery_app.celery beat -l info
~~~

Re-embed jobs:

~~~powershell
.\scripts\reembed.ps1
~~~

The first embedding call downloads the configured local model and caches it in the normal Sentence Transformers cache.

## Tests and verification

Current repository verification commands:

~~~powershell
$env:PYTHONPATH = "backend"
python -m compileall -q backend/app
python -c "from sqlalchemy.orm import configure_mappers; from app.main import app; configure_mappers(); print('backend ok')"

cd frontend
npm ci
npm run lint
npm run build
~~~

The API smoke paths verified during the audit are:

- GET /health
- database schema initialization
- registration
- login
- public faceted job search

There is currently no committed pytest suite. A proper test suite should be the next engineering task, with isolated PostgreSQL fixtures and scraper response fixtures.

## Troubleshooting

### Docker is not running

Start Docker Desktop, then check:

~~~powershell
docker info
docker compose ps
~~~

### Backend says relation does not exist

Run:

~~~powershell
.\scripts\seed.ps1
~~~

Make sure backend/.env points to the same PostgreSQL instance used by Docker.

### Frontend loads but API requests fail

Check both values in frontend/.env.local:

~~~text
NEXT_PUBLIC_API_URL=http://localhost:8000/api
API_URL=http://localhost:8000/api
~~~

Restart the Next.js process after changing env files.

### Redis or Celery cannot connect

The host port is 6380 while the container port is 6379:

~~~powershell
docker compose ps
docker compose logs redis
~~~

### Port is already in use

Find the process:

~~~powershell
Get-NetTCPConnection -LocalPort 3000,8000,5432,6380,7700 -ErrorAction SilentlyContinue
~~~

Stop the old process or change the port mapping in Compose and the matching env value.

### Scraper returns no jobs

Check:

- robots.txt permission
- source response status
- parser selectors or JSON shape
- retry logs
- source registry configuration
- whether the catalog source has a configured endpoint

Do not bypass robots.txt or add credentials to make a scraper work.

### Embedding is slow

This is expected on the first local model load. The model is cached after the first successful call. Use reembed only after changing the model or embedding input text.

### Inspect logs

~~~powershell
.\scripts\logs.ps1
docker compose logs -f postgres redis meilisearch
~~~

## Deployment notes

The production files are:

- docker-compose.prod.yml
- backend/Dockerfile
- frontend/Dockerfile
- Caddyfile
- deploy.sh

Before deployment:

1. create real host-only env files
2. replace JWT_SECRET
3. use a non-default PostgreSQL password
4. configure production CORS origins
5. put the application behind HTTPS
6. run migrations
7. back up PostgreSQL and Docker volumes
8. configure logs and restart policy
9. validate /health after deploy

Do not put passwords, JWT secrets or third-party credentials in GitHub.

## Security boundaries

- Passwords are hashed with Python scrypt and per-user salts.
- JWT tokens have an expiry.
- CORS is allowlist-based.
- Public job and blog HTML is sanitized with Bleach before returning it.
- Scrapers normalize URLs and respect robots.txt.
- Scraper requests use timeouts and retries.
- Search filters use SQLAlchemy expressions rather than string-built SQL.
- Local .env and production env files are ignored by Git.

Autopilot application adapters should only be used with explicit user intent and should be tested against each ATS independently.

## Contributing

Before opening a pull request:

~~~powershell
python -m compileall -q backend/app
cd frontend
npm run lint
npm run build
~~~

Please include:

- what changed
- why it changed
- how it was tested
- migration or env changes
- screenshots for UI changes
- scraper fixtures for parser changes
- rollback notes for production-impacting changes

## Documentation references

The README structure follows practical self-hosting documentation patterns: a short quick start, explicit env examples, health checks, logs, troubleshooting and deployment notes. These topics appear in developer and self-hosting discussions on Reddit, including [self-hosting README guidance](https://www.reddit.com/r/selfhosted/comments/1ta7xwx/selfhosting_best_practices_for_devs/), [Docker env and secret handling](https://www.reddit.com/r/selfhosted/comments/1ftlesr/), [Compose troubleshooting](https://www.reddit.com/r/selfhosted/comments/12n7h09/) and [Docker secret management](https://www.reddit.com/r/selfhosted/comments/1thrv82/).

