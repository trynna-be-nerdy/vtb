#!/usr/bin/env bash
# One-time database initialisation: run Alembic migrations and seed sources.
# Executed by the db_init container in docker-compose on first startup.
set -euo pipefail

echo "[init-db] Waiting for PostgreSQL to be ready..."
until python -c "
import asyncio, asyncpg, os
async def check():
    url = os.environ['DATABASE_URL'].replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(url)
    await conn.close()
asyncio.run(check())
" 2>/dev/null; do
  echo "[init-db] PostgreSQL not ready yet — retrying in 2s..."
  sleep 2
done
echo "[init-db] PostgreSQL is ready."

echo "[init-db] Running Alembic migrations..."
alembic upgrade head
echo "[init-db] Migrations complete."

echo "[init-db] Applying init.sql (triggers)..."
python -c "
import asyncio, asyncpg, os

async def run():
    url = os.environ['DATABASE_URL'].replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(url)
    with open('backend/db/init.sql') as f:
        sql = f.read()
    await conn.execute(sql)
    await conn.close()
    print('[init-db] init.sql applied.')

asyncio.run(run())
"

echo "[init-db] Seeding sources table..."
python -c "
import asyncio, asyncpg, os

SOURCES = [
    {
        'name': 'Loudoun County Board of Supervisors',
        'base_url': 'https://loudoun.gov/meetings',
        'scraper_type': 'loudoun',
        'enabled': True,
    },
    {
        'name': 'Loudoun County Planning Commission',
        'base_url': 'https://loudoun.gov/meetings',
        'scraper_type': 'loudoun',
        'enabled': True,
    },
    {
        'name': 'LCPS School Board',
        'base_url': 'https://lcps.org/boarddocs',
        'scraper_type': 'lcps',
        'enabled': True,
    },
    {
        'name': 'Loudoun County Advisory Boards',
        'base_url': 'https://loudoun.gov/meetings',
        'scraper_type': 'loudoun',
        'enabled': True,
    },
]

async def seed():
    url = os.environ['DATABASE_URL'].replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(url)
    for s in SOURCES:
        await conn.execute(
            '''
            INSERT INTO sources (name, base_url, scraper_type, enabled)
            VALUES (\$1, \$2, \$3, \$4)
            ON CONFLICT (name) DO NOTHING
            ''',
            s['name'], s['base_url'], s['scraper_type'], s['enabled'],
        )
    await conn.close()
    print(f'[init-db] Seeded {len(SOURCES)} sources.')

asyncio.run(seed())
"

echo "[init-db] Initialisation complete."
