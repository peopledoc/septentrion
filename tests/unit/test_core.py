import pytest

from septentrion import configuration, core, exceptions, versions


@pytest.fixture
def known_versions(mocker):
    versions_ = [versions.Version.from_string(v) for v in ("1.1", "1.2", "1.3")]
    mocker.patch("septentrion.core.files.get_known_versions", return_value=versions_)

    return versions_


def test_get_applied_versions(mocker, known_versions):
    mocker.patch(
        "septentrion.core.db.get_applied_versions",
        return_value=[
            versions.Version.from_string("1.0"),
            versions.Version.from_string("1.1"),
        ],
    )
    settings = configuration.Settings.from_cli({})
    versions_ = core.get_applied_versions(settings=settings)

    assert versions_ == [versions.Version.from_string("1.1")]


def test_get_closest_version_unknown_target_version(known_versions):
    settings = configuration.Settings.from_cli(
        {"target_version": versions.Version.from_string("1.5")}
    )

    # target_version is not a known version
    with pytest.raises(ValueError):
        core.get_closest_version(
            settings=settings,
            target_version=versions.Version.from_string("1.5"),
            sql_tpl="schema_{}.sql",
            existing_files=[],
        )


def test_get_closest_version_ok(known_versions):
    settings = configuration.Settings.from_cli({})

    version = core.get_closest_version(
        settings=settings,
        target_version=versions.Version.from_string("1.1"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.0.sql", "schema_1.1.sql"],
    )

    assert version == versions.Version.from_string("1.1")


def test_get_closest_version_schema_doesnt_exist(known_versions):
    settings = configuration.Settings.from_cli({})

    version = core.get_closest_version(
        settings=settings,
        target_version=versions.Version.from_string("1.1"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.0.sql", "schema_1.2.sql"],
    )

    # schema_1.1.sql doesn't exist
    assert version is None


def test_get_closest_version_schema_force_ko(known_versions):
    settings = configuration.Settings.from_cli({})

    with pytest.raises(ValueError):
        core.get_closest_version(
            settings=settings,
            target_version=versions.Version.from_string("1.1"),
            sql_tpl="schema_{}.sql",
            existing_files=["schema_1.0.sql", "schema_1.1.sql"],
            force_version=versions.Version.from_string("1.4"),
        )


def test_get_closest_version_schema_force_ok(known_versions):
    settings = configuration.Settings.from_cli({})

    version = core.get_closest_version(
        settings=settings,
        target_version=versions.Version.from_string("1.3"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.2.sql", "schema_1.3.sql"],
        force_version=versions.Version.from_string("1.2"),
    )

    assert version == versions.Version.from_string("1.2")


def test_get_closest_version_schema_force_dont_exist(known_versions):
    settings = configuration.Settings.from_cli({})

    version = core.get_closest_version(
        settings=settings,
        target_version=versions.Version.from_string("1.3"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.1.sql", "schema_1.3.sql"],
        force_version=versions.Version.from_string("1.2"),
    )

    # schema_1.2.sql doesn't exist
    assert version is None


def test_get_best_schema_version_ok(mocker, known_versions):
    mocker.patch(
        "septentrion.core.files.get_special_files",
        return_value=["schema_1.1.sql", "schema_1.2.sql"],
    )
    settings = configuration.Settings.from_cli(
        {"target_version": versions.Version.from_string("1.2")}
    )

    version = core.get_best_schema_version(settings=settings)

    assert version == versions.Version.from_string("1.2")


def test_get_best_schema_version_ko(mocker, known_versions):
    mocker.patch(
        "septentrion.core.files.get_special_files",
        return_value=["schema_1.0.sql", "schema_1.3.sql"],
    )
    settings = configuration.Settings.from_cli(
        {"target_version": versions.Version.from_string("1.2")}
    )

    assert core.get_best_schema_version(settings=settings) is None


def test_build_migration_plan_unknown_version(known_versions):
    settings = configuration.Settings.from_cli(
        {"target_version": versions.Version.from_string("1.5")}
    )

    with pytest.raises(ValueError):
        list(core.build_migration_plan(settings))


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
    settings = configuration.Settings.from_cli(
        {"target_version": versions.Version.from_string("1.2")}
    )

    plan = core.build_migration_plan(settings=settings)

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
            "version": versions.Version.from_string("1.1"),
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
            "version": versions.Version.from_string("1.2"),
        },
    ]
    assert list(plan) == expected
