from contextlib import contextmanager

import pytest

from septentrion import configuration, db
from septentrion.versions import Version


@pytest.fixture()
def fake_db(mocker):
    @contextmanager
    def execute(response):
        yield response

    def _fake_db(response=None):
        execute_mock = mocker.patch(
            "septentrion.db.execute", return_value=execute(response)
        )
        return execute_mock

    return _fake_db


def test_get_applied_versions(fake_db):
    settings = configuration.Settings.from_cli({})
    fake_db(response=[["1.0"], ["1.1"]])

    result = db.get_applied_versions(settings)

    assert result == [Version.from_string("1.0"), Version.from_string("1.1")]


def test_get_applied_migrations(fake_db):
    settings = configuration.Settings.from_cli({})
    execute_mock = fake_db(response=[["first.sql"], ["second.sql"]])

    result = db.get_applied_migrations(settings, Version.from_string("1.1"))

    assert result == ["first.sql", "second.sql"]
    execute_mock.assert_called_once()
    assert "1.1" in str(execute_mock.call_args)


@pytest.mark.parametrize(
    "applied_versions, current_version",
    [([["1.0"], ["1.1"], ["1.2"]], Version.from_string("1.2")), ([], None)],
)
def test_get_current_schema_version(fake_db, applied_versions, current_version):
    settings = configuration.Settings.from_cli({})
    fake_db(response=applied_versions)

    result = db.get_current_schema_version(settings)

    assert result == current_version


@pytest.mark.parametrize(
    "db_response, initialized", [[iter([True]), True], [iter([]), False]],
)
def test_is_schema_initialized(fake_db, db_response, initialized):
    settings = configuration.Settings.from_cli({})
    fake_db(response=db_response)

    result = db.is_schema_initialized(settings)

    assert result is initialized
