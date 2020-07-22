import os

import psycopg2
import pytest

from septentrion import configuration


def db_params_from_env():
    return {
        "user": os.environ.get("PGUSER"),
        "dbname": os.environ.get("PGDATABASE"),
        "host": os.environ.get("PGHOST"),
        "port": os.environ.get("PGPORT"),
        "password": os.environ.get("PGPASSWORD"),
    }


@pytest.fixture
def db():
    """
    Create a new database for running the test
    Drop it at the end
    """
    connection = psycopg2.connect(dbname="postgres")
    connection.set_session(autocommit=True)
    cursor = connection.cursor()
    test_db_name = "test_septentrion"
    # create test database to running the test
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
    cursor.execute(f"CREATE DATABASE {test_db_name}")

    params = db_params_from_env()
    params["dbname"] = test_db_name
    yield params

    cursor.execute(f"DROP DATABASE {test_db_name}")


@pytest.fixture()
def fake_db(mocker):
    """
    Mutate the return_value property of the fixture to control
    the canned db responses
    """
    fake_execute = mocker.Mock()
    patch = mocker.patch("septentrion.db.execute")
    patch.return_value.__enter__ = fake_execute
    yield fake_execute


@pytest.fixture()
def temporary_directory(tmpdir):
    with tmpdir.as_cwd():
        yield


@pytest.fixture()
def settings_factory():
    def _(**kwargs):
        return configuration.Settings(**kwargs)

    return _
