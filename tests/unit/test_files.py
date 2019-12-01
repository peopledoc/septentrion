import io

import pytest

from septentrion import configuration, files


@pytest.mark.parametrize("isdir,expected", [(True, ["15.0"]), (False, [])])
def test_list_dirs(mocker, isdir, expected):
    mocker.patch("os.listdir", return_value=["15.0"])
    mocker.patch("os.path.isdir", return_value=isdir)

    dirs = files.list_dirs("tests/test_data")

    assert dirs == expected


@pytest.mark.parametrize("isfile,expected", [(True, ["file.sql"]), (False, [])])
def test_list_files(mocker, isfile, expected):
    mocker.patch("os.listdir", return_value=["file.sql"])
    mocker.patch("os.path.isfile", return_value=isfile)

    values = files.list_files("tests/test_data/sql/fixtures")

    assert values == expected


@pytest.mark.parametrize(
    "value,expected", [("/foo/manual/bar", True), ("/blah.tgz", False)]
)
def test_is_manual_migration(value, expected):
    assert files.is_manual_migration(value) == expected


def test_is_manual_migration_true(mocker):
    mocker.patch("io.open", return_value=io.StringIO("--meta-psql:done"))

    assert files.is_manual_migration("/foo.dml.sql") is True


def test_is_manual_migration_false(mocker):
    mocker.patch("io.open", return_value=io.StringIO("foo"))

    assert files.is_manual_migration("/foo.dml.sql") is False


def test_get_known_schemas(mocker):
    mocker.patch("os.listdir", return_value=["schema_17.02.sql", "schema_16.12.sql"])
    settings = configuration.Settings.from_cli(
        {"migrations_root": "tests/test_data/sql", "verbose": 0}
    )

    values = files.get_known_schemas(settings=settings)

    expected = ["schema_16.12.sql", "schema_17.02.sql"]
    assert sorted(values) == expected


def test_get_known_fixtures(mocker):
    mocker.patch("os.listdir", return_value=["fixtures_16.12.sql"])
    settings = configuration.Settings.from_cli(
        {"migrations_root": "tests/test_data/sql", "verbose": 0}
    )

    values = files.get_known_fixtures(settings=settings)

    assert values == ["fixtures_16.12.sql"]


def test_get_known_fixtures_unknown_path(mocker):
    mocker.patch("os.listdir", side_effect=FileNotFoundError())
    settings = configuration.Settings.from_cli(
        {"migrations_root": "tests/test_data/sql", "verbose": 0}
    )

    values = files.get_known_fixtures(settings=settings)

    assert values == []


def test_get_known_versions(mocker):
    mocker.patch("septentrion.files.list_dirs", return_value=["16.11", "16.12", "16.9"])
    mocker.patch("os.path.islink", return_value=False)
    settings = configuration.Settings.from_cli({"migrations_root": ""})

    values = files.get_known_versions(settings=settings)

    assert values == ["16.9", "16.11", "16.12"]


def test_get_known_versions_error(mocker):
    mocker.patch("septentrion.files.list_dirs", side_effect=OSError)
    settings = configuration.Settings.from_cli({"migrations_root": ""})

    with pytest.raises(ValueError):
        files.get_known_versions(settings=settings)


def test_get_migrations_files_mapping_ok(mocker):
    mocker.patch(
        "septentrion.files.list_files",
        return_value=["file.sql", "file.dml.sql", "file.ddl.sql"],
    )
    settings = configuration.Settings.from_cli(
        {"migrations_root": "tests/test_data/sql", "verbose": 0}
    )

    values = files.get_migrations_files_mapping(settings=settings, version="17.1")

    assert values == {
        "file.dml.sql": "tests/test_data/sql/17.1/manual/file.dml.sql",
        "file.ddl.sql": "tests/test_data/sql/17.1/manual/file.ddl.sql",
    }


def test_get_migrations_files_mapping_ko(mocker):
    mocker.patch("septentrion.files.list_files", side_effect=OSError)

    settings = configuration.Settings.from_cli(
        {"migrations_root": "tests/test_data/sql", "verbose": 0}
    )

    with pytest.raises(ValueError):
        files.get_migrations_files_mapping(settings=settings, version="17.1")
