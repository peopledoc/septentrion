import pytest

from septentrion import core, exceptions, settings


@pytest.fixture
def known_versions(mocker):
    versions = ["1.1", "1.2", "1.3"]
    mocker.patch("septentrion.core.files.get_known_versions", return_value=versions)

    return versions


def test_get_applied_versions(mocker, known_versions):
    mocker.patch(
        "septentrion.core.db.get_applied_versions", return_value=["1.0", "1.1"]
    )

    versions = core.get_applied_versions()

    assert versions == ["1.1"]


def test_get_closest_version_unknown_target_version(known_versions):
    settings.consolidate(target_version="1.5", verbose=0)

    # target_version is not a known version
    with pytest.raises(ValueError):
        core.get_closest_version("1.5", "schema_{}.sql", [])


def test_get_closest_version_ok(known_versions):
    version = core.get_closest_version(
        "1.1", "schema_{}.sql", ["schema_1.0.sql", "schema_1.1.sql"]
    )

    assert version == "1.1"


def test_get_closest_version_schema_dont_exists(known_versions):
    version = core.get_closest_version(
        "1.1", "schema_{}.sql", ["schema_1.0.sql", "schema_1.2.sql"]
    )

    # schema_1.1.sql doesn't exist
    assert version is None


def test_get_closest_version_schema_force_ko(known_versions):
    with pytest.raises(ValueError):
        core.get_closest_version(
            "1.1",
            "schema_{}.sql",
            ["schema_1.0.sql", "schema_1.1.sql"],
            force_version="1.4",
        )


def test_get_closest_version_schema_force_ok(known_versions):
    version = core.get_closest_version(
        "1.3",
        "schema_{}.sql",
        ["schema_1.2.sql", "schema_1.3.sql"],
        force_version="1.2",
    )

    assert version == "1.2"


def test_get_closest_version_schema_force_dont_exist(known_versions):
    version = core.get_closest_version(
        "1.3",
        "schema_{}.sql",
        ["schema_1.1.sql", "schema_1.3.sql"],
        force_version="1.2",
    )

    # schema_1.2.sql doesn't exist
    assert version is None


def test_get_best_schema_version_ok(mocker, known_versions):
    mocker.patch(
        "septentrion.core.files.get_known_schemas",
        return_value=["schema_1.1.sql", "schema_1.2.sql"],
    )
    settings.consolidate(
        target_version="1.2",
        schema_template="schema_{}.sql",
        schema_version=None,
        verbose=0,
    )

    version = core.get_best_schema_version()

    assert version == "1.2"


def test_get_best_schema_version_ko(mocker, known_versions):
    mocker.patch(
        "septentrion.core.files.get_known_schemas",
        return_value=["schema_1.0.sql", "schema_1.3.sql"],
    )
    settings.consolidate(
        target_version="1.2",
        schema_template="schema_{}.sql",
        schema_version=None,
        verbose=0,
    )

    with pytest.raises(exceptions.SeptentrionException):
        core.get_best_schema_version()


def test_build_migration_plan_unknown_version(known_versions):
    settings.consolidate(target_version="1.5", verbose=0)

    with pytest.raises(ValueError):
        list(core.build_migration_plan())


def test_build_migration_plan_ok(mocker, known_versions):
    mocker.patch("septentrion.core.db.get_applied_migrations", return_value=[])
    mocker.patch(
        "septentrion.core.files.get_migrations_files_mapping",
        return_value={
            "file.ddl.sql": "tests/test_data/sql/17.1/manual/file.ddl.sql",
            "file.dml.sql": "tests/test_data/sql/17.1/manual/file.dml.sql",
        },
    )
    mocker.patch("septentrion.core.files.is_manual_migration", return_value=True)
    settings.consolidate(target_version="1.2", verbose=0)

    plan = core.build_migration_plan()

    expected = [
        {
            "plan": [
                (
                    "file.ddl.sql",
                    False,
                    "tests/test_data/sql/17.1/manual/file.ddl.sql",
                    True,
                ),
                (
                    "file.dml.sql",
                    False,
                    "tests/test_data/sql/17.1/manual/file.dml.sql",
                    True,
                ),
            ],
            "version": "1.1",
        },
        {
            "plan": [
                (
                    "file.ddl.sql",
                    False,
                    "tests/test_data/sql/17.1/manual/file.ddl.sql",
                    True,
                ),
                (
                    "file.dml.sql",
                    False,
                    "tests/test_data/sql/17.1/manual/file.dml.sql",
                    True,
                ),
            ],
            "version": "1.2",
        },
    ]
    assert list(plan) == expected
