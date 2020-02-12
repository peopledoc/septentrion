import pathlib
from unittest.mock import call

from septentrion import configuration, versions
from septentrion.core import get_best_schema_version
from septentrion.migrate import init_schema


def test_init_schema(mocker):
    patch = mocker.patch("septentrion.migrate.run_script",)

    settings = configuration.Settings.from_cli(
        {
            "host": "",
            "port": "",
            "username": "",
            "dbname": "",
            "migrations_root": "example_migrations",
            "target_version": versions.Version.from_string("1.1"),
        }
    )

    init_schema(
        settings=settings, init_version=get_best_schema_version(settings=settings)
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
    patch = mocker.patch("septentrion.migrate.run_script",)

    settings = configuration.Settings.from_cli(
        {
            "host": "",
            "port": "",
            "username": "",
            "dbname": "",
            "migrations_root": "example_migrations",
            "additional_schema_file": ["extra_file.sql"],
            "before_schema_file": ["before_file.sql"],
            "after_schema_file": ["after_file.sql"],
            "target_version": versions.Version.from_string("1.1"),
        }
    )

    init_schema(
        settings=settings, init_version=get_best_schema_version(settings=settings)
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
