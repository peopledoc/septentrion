import os

import psycopg2
import pytest
from psycopg2 import sql


@pytest.fixture
def db():
    """
    Create a new database for running the test
    Drop it at the end
    """
    settings = {
        "host": os.environ.get("PGHOST"),
        "port": os.environ.get("PGPORT"),
        "user": os.environ.get("PGUSER"),
        "password": os.environ.get("PGPASSWORD"),
    }
    for key, value in settings.items():
        assert value is not None, "PG{} need to be defined".format(key.upper())

    # default database to connect to
    settings["dbname"] = "postgres"
    connection = psycopg2.connect(**settings)
    connection.set_session(autocommit=True)
    cursor = connection.cursor()

    # create test database to running the test
    settings["dbname"] = "test_septentrion"
    cursor.execute(
        sql.SQL("CREATE DATABASE {}").format(sql.Identifier(settings["dbname"]))
    )

    yield settings

    cursor.execute(
        sql.SQL("DROP DATABASE {}").format(sql.Identifier(settings["dbname"]))
    )
