import pytest

from septentrion import configuration, db
from septentrion.versions import Version


def test_get_applied_versions(fake_db):
    settings = configuration.Settings()
    fake_db.return_value = [["1.0"], ["1.1"]]

    result = db.get_applied_versions(settings)

    assert result == [Version.from_string("1.0"), Version.from_string("1.1")]


def test_get_applied_migrations(fake_db):
    settings = configuration.Settings()
    fake_db.return_value = [["first.sql"], ["second.sql"]]

    result = db.get_applied_migrations(settings, Version.from_string("1.1"))

    assert result == ["first.sql", "second.sql"]
    fake_db.assert_called_once()


@pytest.mark.parametrize(
    "applied_versions, current_version",
    [([["1.0"], ["1.1"], ["1.2"]], Version.from_string("1.2")), ([], None)],
)
def test_get_current_schema_version(fake_db, applied_versions, current_version):
    settings = configuration.Settings()
    fake_db.return_value = applied_versions

    result = db.get_current_schema_version(settings)

    assert result == current_version


@pytest.mark.parametrize(
    "db_responses, initialized",
    [
        [[iter([[True]]), iter([True])], True],
        [[iter([[True]]), iter([])], False],
        [[iter([[False]]), iter([True])], False],
    ],
)
def test_is_schema_initialized(fake_db, db_responses, initialized):
    settings = configuration.Settings()
    fake_db.side_effect = db_responses

    result = db.is_schema_initialized(settings)

    assert result is initialized
