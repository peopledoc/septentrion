import os

HOST = os.getenv("PGHOST", "localhost")
PORT = os.getenv("PGPORT", 5432)
USER = os.getenv("PGUSER", "postgres")
PASSWORD = os.getenv("PGPASSWORD", "my")
DATABASE = os.getenv("PGDATABASE", "postgres")
MIGRATIONS_ROOT = os.getenv("MIGRATIONS_FOLDER", "migrations")
TARGET_VERSION = os.getenv("TARGET_VERSION", "16.12")
SCHEMA_TPL = 'schema_{}.sql'
FIXTURES_TPL = 'fixtures_{}.sql'


TABLE = "west_migrations"
