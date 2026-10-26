-- Mounted by docker-compose.dev.yml into the Postgres entrypoint.
-- These are the extensions scripts/init_db.py also creates.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS btree_gist;
