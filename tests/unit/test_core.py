import pathlib

import pytest

from septentrion import configuration, core, exceptions
from septentrion.versions import Version


@pytest.fixture
def known_versions(mocker):
    versions_ = [Version.from_string(v) for v in ("0", "1.1", "1.2", "1.3")]
    mocker.patch("septentrion.core.files.get_known_versions", return_value=versions_)

    return versions_


def test_get_applied_versions(mocker, known_versions):
    mocker.patch(
        "septentrion.core.db.get_applied_versions",
        return_value=[
            Version.from_string("1.0"),
            Version.from_string("1.1"),
        ],
    )
    settings = configuration.Settings()
    versions_ = core.get_applied_versions(settings=settings)

    assert versions_ == [Version.from_string("1.1")]


def test_get_closest_version_unknown_target_version(known_versions):
    settings = configuration.Settings(target_version=Version.from_string("1.5"))

    # target_version is not a known version
    with pytest.raises(ValueError):
        core.get_closest_version(
            settings=settings,
            target_version=Version.from_string("1.5"),
            sql_tpl="schema_{}.sql",
            existing_files=[],
        )


def test_get_closest_version_ok(known_versions):
    settings = configuration.Settings()

    version = core.get_closest_version(
        settings=settings,
        target_version=Version.from_string("1.1"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.0.sql", "schema_1.1.sql"],
    )

    assert version == Version.from_string("1.1")


def test_get_closest_version_schema_doesnt_exist(known_versions):
    settings = configuration.Settings()

    version = core.get_closest_version(
        settings=settings,
        target_version=Version.from_string("1.1"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.0.sql", "schema_1.2.sql"],
    )

    # schema_1.1.sql doesn't exist
    assert version is None


def test_get_closest_version_earlier_schema(known_versions):
    settings = configuration.Settings()

    version = core.get_closest_version(
        settings=settings,
        target_version=Version.from_string("1.3"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.0.sql", "schema_1.1.sql"],
        force_version=Version.from_string("1.2"),
    )

    assert version is None


def test_get_closest_version_schema_force_ko(known_versions):
    """
    Will fail because "1.4" is unknown
    """
    settings = configuration.Settings()

    with pytest.raises(ValueError):
        core.get_closest_version(
            settings=settings,
            target_version=Version.from_string("1.1"),
            sql_tpl="schema_{}.sql",
            existing_files=["schema_1.0.sql", "schema_1.1.sql"],
            force_version=Version.from_string("1.4"),
        )


def test_get_closest_version_schema_force_ok(known_versions):
    settings = configuration.Settings()

    version = core.get_closest_version(
        settings=settings,
        target_version=Version.from_string("1.3"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.2.sql", "schema_1.3.sql"],
        force_version=Version.from_string("1.2"),
    )

    assert version == Version.from_string("1.2")


def test_get_closest_version_schema_force_dont_exist(known_versions):
    settings = configuration.Settings()

    version = core.get_closest_version(
        settings=settings,
        target_version=Version.from_string("1.3"),
        sql_tpl="schema_{}.sql",
        existing_files=["schema_1.1.sql", "schema_1.3.sql"],
        force_version=Version.from_string("1.2"),
    )

    # schema_1.2.sql doesn't exist
    assert version is None


def test_get_best_schema_version_ok(mocker, known_versions):
    mocker.patch(
        "septentrion.core.files.get_special_files",
        return_value=["schema_1.1.sql", "schema_1.2.sql"],
    )
    settings = configuration.Settings(target_version=Version.from_string("1.2"))

    version = core.get_best_schema_version(settings=settings)

    assert version == Version.from_string("1.2")


def test_get_best_schema_version_ko(mocker, known_versions):
    mocker.patch(
        "septentrion.core.files.get_special_files",
        return_value=["schema_1.0.sql", "schema_1.3.sql"],
    )
    settings = configuration.Settings(target_version=Version.from_string("1.2"))

    with pytest.raises(exceptions.SeptentrionException):
        core.get_best_schema_version(settings=settings)


def test_build_migration_plan_unknown_version(known_versions):
    settings = configuration.Settings(target_version=Version.from_string("1.5"))
    from_version = Version.from_string("0")

    with pytest.raises(ValueError):
        list(core.build_migration_plan(settings, from_version=from_version))


def test_build_migration_plan_db(mocker, known_versions):
    # What a mock hell ><

    # So first, we mock db.get_applied_migrations to tell the following story:
    # - on 1.1, only migration "a" was previously applied.
    # - on 1.2, no migration was previously applied.
    mocker.patch(
        "septentrion.db.get_applied_migrations",
        side_effect=lambda settings, version: {
            Version.from_string("1.1"): ["a"],
            Version.from_string("1.2"): [],
        }[version],
    )
    # Then, regarding the migration files that exist on the disk:
    # - There are 2 files for 1.1 (so one already applied and one new)
    # - 1 file for 1.2
    # - 1 file for 1.3
    mocker.patch(
        "septentrion.files.get_migrations_files_mapping",
        side_effect=lambda settings, version: {
            Version.from_string("1.1"): {
                "a": pathlib.Path("a"),
                "b": pathlib.Path("b"),
            },
            Version.from_string("1.2"): {
                "c": pathlib.Path("c"),
            },
            Version.from_string("1.3"): {"d": pathlib.Path("d")},
        }[version],
    )
    # The contents of each migration is ignored
    mocker.patch("septentrion.files.file_lines_generator", return_value="")
    # Migration "c" is a manual migration
    mocker.patch(
        "septentrion.files.is_manual_migration",
        side_effect=(
            lambda migration_path, migration_contents: str(migration_path) == "c"
        ),
    )
    # We'll apply migrations up until 1.2 included
    settings = configuration.Settings(
        target_version=Version.from_string("1.2"),
    )
    # And we'll start at version 1.1 included
    from_version = Version.from_string("1.1")
    plan = core.build_migration_plan(settings=settings, from_version=from_version)

    expected = [
        {
            "version": Version.from_string("1.1"),
            "plan": [
                # On 1.1, migration a is already applied. It's not manual
                ("a", True, pathlib.Path("a"), False),
                # migration b, though needs to be applied. It's not manual
                ("b", False, pathlib.Path("b"), False),
            ],
        },
        {
            "version": Version.from_string("1.2"),
            "plan": [
                # migration c also needs to be applied. It's manual (the last True)
                ("c", False, pathlib.Path("c"), True),
            ],
        },
    ]

    assert list(plan) == expected


def test_build_migration_plan_with_schema(mocker, known_versions):
    mocker.patch("septentrion.core.db.get_applied_migrations", return_value=[])
    settings = configuration.Settings(target_version="1.2")
    from_version = Version.from_string("1.1")

    plan = list(core.build_migration_plan(settings=settings, from_version=from_version))

    expected = [
        {"plan": [], "version": Version.from_string("1.1")},
        {"plan": [], "version": Version.from_string("1.2")},
    ]
    assert list(plan) == expected


def test_build_migration_plan_with_no_target_version(mocker, known_versions):
    mocker.patch("septentrion.core.db.get_applied_migrations", return_value=[])
    settings = configuration.Settings(target_version=None)
    from_version = Version.from_string("1.1")

    plan = list(core.build_migration_plan(settings=settings, from_version=from_version))

    expected = [
        {"plan": [], "version": Version.from_string("1.1")},
        {"plan": [], "version": Version.from_string("1.2")},
        {"plan": [], "version": Version.from_string("1.3")},
    ]
    assert list(plan) == expected
