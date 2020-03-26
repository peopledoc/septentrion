import pathlib

import pytest

from septentrion import configuration, exceptions, files, versions


@pytest.mark.parametrize(
    "migration_path,migration_contents,expected",
    [
        ("/foo/manual/bar", [], True),
        ("/foo.dml.sql", ["--meta-psql:done"], True),
        ("/blah.tgz", [], False),
        ("/foo.dml.sql", ["foo"], False),
    ],
)
def test_is_manual_migration(migration_path, migration_contents, expected):
    assert (
        files.is_manual_migration(
            migration_path=pathlib.Path(migration_path),
            migration_contents=migration_contents,
        )
        == expected
    )


def test_get_special_files(mocker):
    mocker.patch(
        "septentrion.files.iter_files",
        return_value=[
            pathlib.Path("schema_17.02.sql"),
            pathlib.Path("schema_16.12.sql"),
        ],
    )

    values = files.get_special_files(
        root=pathlib.Path("tests/test_data/sql"), folder="schemas"
    )

    expected = ["schema_16.12.sql", "schema_17.02.sql"]
    assert sorted(values) == expected


def test_get_known_versions(mocker):
    mocker.patch(
        "septentrion.files.iter_dirs",
        return_value=[
            pathlib.Path("16.11"),
            pathlib.Path("16.12"),
            pathlib.Path("16.9"),
        ],
    )
    settings = configuration.Settings()

    values = files.get_known_versions(settings=settings)

    assert values == [
        versions.Version.from_string("16.9"),
        versions.Version.from_string("16.11"),
        versions.Version.from_string("16.12"),
    ]


def test_get_known_versions_error(mocker):
    mocker.patch("septentrion.files.iter_dirs", side_effect=OSError)
    settings = configuration.Settings()

    with pytest.raises(exceptions.SeptentrionException):
        files.get_known_versions(settings=settings)


def test_get_migrations_files_mapping(mocker):
    mocker.patch(
        "septentrion.files.iter_files",
        return_value=[
            pathlib.Path("tests/test_data/sql/17.1/manual/file.sql"),
            pathlib.Path("tests/test_data/sql/17.1/manual/file.dml.sql"),
            pathlib.Path("tests/test_data/sql/17.1/manual/file.ddl.sql"),
        ],
    )
    settings = configuration.Settings(
        migrations_root="tests/test_data/sql", ignore_symlinks=True
    )

    values = files.get_migrations_files_mapping(
        settings=settings, version=versions.Version.from_string("17.1")
    )

    assert values == {
        "file.dml.sql": pathlib.Path("tests/test_data/sql/17.1/manual/file.dml.sql"),
        "file.ddl.sql": pathlib.Path("tests/test_data/sql/17.1/manual/file.ddl.sql"),
    }
