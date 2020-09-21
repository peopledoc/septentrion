import datetime

import psycopg2.errors
import pytest

from septentrion import db as db_module
from septentrion import versions


def test_execute(db, settings_factory):
    settings = settings_factory(**db)
    with db_module.execute(settings=settings, query="SELECT 1;") as cursor:
        assert cursor.fetchall() == [[1]]


def test_execute_sql_injection(db, settings_factory):
    settings = settings_factory(**db, table='"pg_enum"; -- SQLi')
    with pytest.raises(psycopg2.errors.UndefinedTable) as exc_info:
        with db_module.execute(
            settings=settings, query="SELECT * FROM {table};"
        ) as cursor:
            assert cursor.fetchall() == [[1]]

    assert 'relation ""pg_enum"; -- SQLi" does not exist' in str(exc_info.value)


def test_write_migration(db, settings_factory):
    settings = settings_factory(**db)
    db_module.create_table(settings=settings)

    db_module.write_migration(
        settings=settings,
        version=versions.Version.from_string("1.2.3"),
        name="some_migration.sql",
    )

    now = datetime.datetime.now(tz=datetime.timezone.utc)

    with db_module.Query(settings=settings, query="SELECT * FROM {table}") as cur:
        id, version, name, date = list(cur)[0]

    assert id == 1
    assert version == "1.2.3"
    assert name == "some_migration.sql"
    one_sec = datetime.timedelta(seconds=1)
    assert now - one_sec < date < now + one_sec
