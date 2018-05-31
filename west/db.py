from contextlib import contextmanager
from distutils.version import StrictVersion

import psycopg2
from psycopg2.extras import DictCursor


def get_connection(settings):
    return psycopg2.connect(
        host=settings.HOST,
        port=settings.PORT,
        dbname=settings.DATABASE,
        user=settings.USER,
        password=settings.PASSWORD)


@contextmanager
def execute(settings, query, args=tuple(), commit=False):
    query = ' '.join(query.format(table=settings.TABLE).split())
    with get_connection(settings) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, args)
            yield cur
        if commit:
            conn.commit()


class Query(object):
    def __init__(self, settings, query, args=tuple(), commit=False):
        self.context_manager = execute(settings, query, args, commit)

    def __enter__(self):
        return self.context_manager.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.context_manager.__exit__(exc_type, exc_val, exc_tb)

    def __call__(self):
        with self:
            pass


query_create_table = """
CREATE TABLE IF NOT EXISTS "{table}" (
    id BIGSERIAL PRIMARY KEY,
    version TEXT,
    name TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
"""

query_max_version = """SELECT DISTINCT "version" FROM "{table}" """

query_write_migration = """
    INSERT INTO "{table}" ("version", "name")
    VALUES (%s, %s)
"""

query_get_applied_migrations = """
    SELECT name, version FROM "{table}"
"""


def get_schema_version(settings):
    with Query(settings, query_max_version) as cur:
        return max(StrictVersion(row[0]) for row in cur)


def get_applied_migrations(settings):
    with Query(settings, query_get_applied_migrations) as cur:
        return [dict(row) for row in cur]


def create_table(settings):
    Query(settings,
          query_create_table,
          commit=True)()


def write_migration(settings, version, name):
    Query(settings, query_write_migration,
          (version, name))()
