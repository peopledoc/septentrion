import os

HOST = os.getenv("PGHOST", "localhost")
PORT = os.getenv("PGPORT", 5432)
USER = os.getenv("PGUSER", "postgres")
PASSWORD = os.getenv("PGPASSWORD", "my")
DATABASE = os.getenv("PGDATABASE", "postgres")

TABLE = "west_migrations"
