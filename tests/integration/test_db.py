import psycopg2.errors
import pytest

from septentrion import db as db_module


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
