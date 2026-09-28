#!/bin/bash
set -e

echo "=== WorkSync Deploy ==="

# Provjeri .env fajlove
for f in .env.prod backend/.env.prod frontend/.env.prod; do
    if [ ! -f "$f" ]; then
        echo "❌ Nedostaje $f"
        exit 1
    fi
done

# Build images
echo "▶ Building images..."
docker compose -f docker-compose.prod.yml build --pull

# Migracije
echo "▶ Pokretanje Postgres-a..."
docker compose -f docker-compose.prod.yml up -d postgres redis meilisearch
sleep 10

echo "▶ Alembic migracije..."
docker compose -f docker-compose.prod.yml run --rm api alembic upgrade head

# Postgres ekstenzije
echo "▶ Postgres ekstenzije..."
docker compose -f docker-compose.prod.yml exec -T postgres psql -U worksync -d worksync -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker compose -f docker-compose.prod.yml exec -T postgres psql -U worksync -d worksync -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
docker compose -f docker-compose.prod.yml exec -T postgres psql -U worksync -d worksync -c "CREATE EXTENSION IF NOT EXISTS unaccent;"

# Start sve
echo "▶ Start sve servise..."
docker compose -f docker-compose.prod.yml up -d

echo "✅ Deploy gotov!"
docker compose -f docker-compose.prod.yml ps