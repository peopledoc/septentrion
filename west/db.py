import psycopg2
from distutils.version import StrictVersion


def get_connection(settings):
    return psycopg2.connect(
        host=settings.HOST,
        port=settings.PORT,
        dbname=settings.DATABASE,
        user=settings.USER,
        password=settings.PASSWORD)


def execute(settings, query, args=tuple(), commit=False):
    with get_connection(settings) as conn:
        with conn.cursor() as cur:
            cur.execute(query.replace("\n", " "), args)
        if commit:
            conn.commit()


def execute_result(settings, query, args=tuple(), commit=False):
    with get_connection(settings) as conn:
        with conn.cursor() as cur:
            cur.execute(query.replace("\n", " "), args)
            for e in cur:
                yield e
        if commit:
            conn.commit()


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


def get_schema_version(settings):
    result = execute_result(settings,
                            query_max_version.format(table=settings.TABLE))
    return max(StrictVersion(row[0]) for row in result)


def create_table(settings):
    execute(settings,
            query_create_table.format(table=settings.TABLE),
            commit=True)


def write_migration(settings, version, name):
    execute(settings, query_write_migration.format(table=settings.TABLE),
            (version, name))
