import pathlib
from unittest.mock import call

from septentrion import configuration, core, migration, versions


def test_init_schema(mocker):
    patch = mocker.patch("septentrion.migration.run_script")

    settings = configuration.Settings(
        host="",
        port="",
        username="",
        dbname="",
        migrations_root="example_migrations",
        target_version=versions.Version.from_string("1.1"),
    )

    migration.init_schema(
        settings=settings, init_version=core.get_best_schema_version(settings=settings)
    )

    calls = [
        call(
            settings=settings,
            path=pathlib.Path("example_migrations/schemas/schema_0.1.sql"),
        ),
        call(
            settings=settings,
            path=pathlib.Path("example_migrations/fixtures/fixtures_0.1.sql"),
        ),
    ]
    assert calls == patch.call_args_list


def test_init_schema_extra_files(mocker):
    patch = mocker.patch("septentrion.migration.run_script")

    settings = configuration.Settings(
        host="",
        port="",
        username="",
        dbname="",
        migrations_root="example_migrations",
        additional_schema_file=["extra_file.sql"],
        before_schema_file=["before_file.sql"],
        after_schema_file=["after_file.sql"],
        target_version=versions.Version.from_string("1.1"),
    )

    migration.init_schema(
        settings=settings, init_version=core.get_best_schema_version(settings=settings)
    )

    calls = [
        call(
            settings=settings,
            path=pathlib.Path("example_migrations/schemas/before_file.sql"),
        ),
        call(
            settings=settings,
            path=pathlib.Path("example_migrations/schemas/extra_file.sql"),
        ),
        call(
            settings=settings,
            path=pathlib.Path("example_migrations/schemas/schema_0.1.sql"),
        ),
        call(
            settings=settings,
            path=pathlib.Path("example_migrations/schemas/after_file.sql"),
        ),
        call(
            settings=settings,
            path=pathlib.Path("example_migrations/fixtures/fixtures_0.1.sql"),
        ),
    ]
    assert calls == patch.call_args_list


def test_migrate(mocker):
    mock_run_script = mocker.patch("septentrion.migration.run_script")
    mocker.patch("septentrion.db.is_schema_initialized", return_value=False)
    mock_init_schema = mocker.patch("septentrion.migration.init_schema")
    mocker.patch("septentrion.db.write_migration")

    mocker.patch(
        "septentrion.migration.core.build_migration_plan",
        return_value=[
            {
                "version": versions.Version(
                    version_tuple=(0, 1), original_string="0.1"
                ),
                "plan": [],
            },
            {
                "version": versions.Version(
                    version_tuple=(1, 0), original_string="1.0"
                ),
                "plan": [
                    (
                        "1.0-0-version-dml.sql",
                        False,
                        "example_migrations/1.0/1.0-0-version-dml.sql",
                        False,
                    ),
                    (
                        "1.0-author-1-ddl.sql",
                        False,
                        "example_migrations/1.0/1.0-author-1-ddl.sql",
                        False,
                    ),
                    (
                        "1.0-author-2-dml.sql",
                        False,
                        "example_migrations/1.0/1.0-author-2-dml.sql",
                        False,
                    ),
                    (
                        "1.0-book-1-ddl.sql",
                        False,
                        "example_migrations/1.0/1.0-book-1-ddl.sql",
                        False,
                    ),
                    (
                        "1.0-book-2-dml.sql",
                        False,
                        "example_migrations/1.0/1.0-book-2-dml.sql",
                        False,
                    ),
                ],
            },
            {
                "version": versions.Version(
                    version_tuple=(1, 1), original_string="1.1"
                ),
                "plan": [
                    (
                        "1.1-0-version-dml.sql",
                        False,
                        "example_migrations/1.1/1.1-0-version-dml.sql",
                        False,
                    ),
                    (
                        "1.1-add-num-pages-1-ddl.sql",
                        False,
                        "example_migrations/1.1/1.1-add-num-pages-1-ddl.sql",
                        False,
                    ),
                    (
                        "1.1-add-num-pages-2-dml.sql",
                        False,
                        "example_migrations/1.1/1.1-add-num-pages-2-dml.sql",
                        False,
                    ),
                    (
                        "1.1-index-ddl.sql",
                        False,
                        "example_migrations/1.1/1.1-index-ddl.sql",
                        False,
                    ),
                ],
            },
        ],
    )

    settings = configuration.Settings(
        host="",
        port="",
        username="",
        dbname="",
        migrations_root="example_migrations",
        target_version=versions.Version.from_string("1.1"),
    )

    migration.migrate(settings=settings)

    mock_init_schema.assert_called_once()
    assert mock_run_script.call_args_list == [
        call(path="example_migrations/1.0/1.0-0-version-dml.sql", settings=settings),
        call(path="example_migrations/1.0/1.0-author-1-ddl.sql", settings=settings),
        call(path="example_migrations/1.0/1.0-author-2-dml.sql", settings=settings),
        call(path="example_migrations/1.0/1.0-book-1-ddl.sql", settings=settings),
        call(path="example_migrations/1.0/1.0-book-2-dml.sql", settings=settings),
        call(path="example_migrations/1.1/1.1-0-version-dml.sql", settings=settings),
        call(
            path="example_migrations/1.1/1.1-add-num-pages-1-ddl.sql", settings=settings
        ),
        call(
            path="example_migrations/1.1/1.1-add-num-pages-2-dml.sql", settings=settings
        ),
        call(path="example_migrations/1.1/1.1-index-ddl.sql", settings=settings),
    ]
