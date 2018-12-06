"""
Interact with the migrations table.
"""

import logging
from contextlib import contextmanager
from distutils.version import StrictVersion

import psycopg2
from psycopg2.extras import DictCursor

from septentrion.settings import settings

logger = logging.getLogger(__name__)


def get_connection():
    """
    Opens a PostgreSQL connection using psycopg2.
    """
    # Note that psycopg2 is responsible for using environment variables and reading
    # ~/.pgpass for all undefined arguments. Because of this, it's important to exclude
    # arguments that we explicitely don't have.

    # Transform settings names into the ones expected by psycopg2
    kwargs = {}
    mapping = {
        "HOST": "host",
        "PORT": "port",
        "DBNAME": "dbname",
        "USERNAME": "user",
        "PASSWORD": "password",
    }
    for name, psycopg_name in mapping.items():
        value = getattr(settings, name)
        if value:
            kwargs[psycopg_name] = value

    connection = psycopg2.connect(**kwargs)

    # Autocommit=true means we'll have more control over when the code is commited
    # (even if this sounds strange)
    connection.set_session(autocommit=True)
    return connection


@contextmanager
def execute(query, args=tuple(), commit=False):
    query = " ".join(query.format(table=settings.TABLE).split())
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            logger.debug("Executing %s -- Args: %s", query, args)
            cur.execute(query, args)
            yield cur
        if commit:
            conn.commit()


class Query(object):
    def __init__(self, query, args=tuple(), commit=False):
        self.context_manager = execute(query, args, commit)

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
    SELECT name FROM "{table}" WHERE "version" = %s
"""

query_is_schema_initialized = """
    SELECT TRUE FROM "{table}" LIMIT 1
"""


def get_current_schema_version():
    versions = get_applied_versions()
    if not versions:
        return None
    return max(StrictVersion(version) for version in versions)


def get_applied_versions():
    with Query(query_max_version) as cur:
        return [row[0] for row in cur]


def get_applied_migrations(version):
    with Query(query_get_applied_migrations, (version,)) as cur:
        return [row[0] for row in cur]


def is_schema_initialized():
    with Query(query_is_schema_initialized) as cur:
        try:
            return next(cur)
        except StopIteration:
            return False


def create_table():
    Query(query_create_table, commit=True)()


def write_migration(version, name):
    Query(query_write_migration, (version, name), commit=True)()
