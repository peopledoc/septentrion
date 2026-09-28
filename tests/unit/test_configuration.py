import pathlib
from io import StringIO

import pytest

from septentrion import configuration, exceptions, versions


def test_get_config_settings():
    config = """
        [septentrion]
        table = north_migrations
    """
    s = configuration.parse_configuration_file(config)

    assert s == {"table": "north_migrations"}


def test_get_config_settings_no_section():
    config = """
        [east]
        table = north_migrations
    """
    with pytest.raises(exceptions.NoSeptentrionSection):
        configuration.parse_configuration_file(config)


def test_settings_init():
    s = configuration.Settings(foo="blah")

    assert s.FOO == "blah"


@pytest.mark.parametrize("verbosity,expected", [(0, 40), (3, 10), (4, 10)])
def test_log_level(verbosity, expected):
    assert configuration.log_level(verbosity) == expected


def test_get_config_files_settings():
    config = """
        [septentrion]
        additional_schema_file=
            more.sql
            another.sql
        before_schema_file=
            before.sql
            another_before.sql
        after_schema_file=
            after.sql
            another_after.sql
    """
    s = configuration.parse_configuration_file(config)

    assert s == {
        "additional_schema_file": ["more.sql", "another.sql"],
        "before_schema_file": ["before.sql", "another_before.sql"],
        "after_schema_file": ["after.sql", "another_after.sql"],
    }


def test_load_configuration_files_no_file(mocker):
    # There's no available file
    mocker.patch(
        "septentrion.configuration.read_default_configuration_files",
        side_effect=exceptions.NoDefaultConfiguration,
    )
    s = configuration.load_configuration_files(value=None)
    assert s == {}


@pytest.mark.parametrize(
    "conf, expected, has_warning",
    [
        ("", {}, True),
        ("[stuff]", {}, True),
        ("[septentrion]\na = b", {"a": "b"}, False),
    ],
)
def test_load_configuration_files_value(caplog, conf, expected, has_warning):
    value = StringIO(conf)
    value.seek(0)
    # Reminder: an empty StringIO is not considered as Falsy.
    s = configuration.load_configuration_files(value=value)
    assert s == expected

    warnings = [r for r in caplog.records if r.levelname == "WARNING"]
    assert bool(warnings) is has_warning
    assert all(
        ["at stdin but contains no septentrion section" in r.message for r in warnings]
    )


def test_load_configuration_files_value_from_file(caplog, mocker):
    with open(
        pathlib.Path(__file__).parents[2] / "tests/test_data/config_file.ini") as f:
        configuration.load_configuration_files(value=f)


@pytest.mark.parametrize(
    "conf, filename, expected, has_warning",
    [
        ("", "setup.cfg", {}, False),
        ("[stuff]", "setup.cfg", {}, False),
        ("[septentrion]\na = b", "setup.cfg", {"a": "b"}, False),
        ("", "septentrion.ini", {}, True),
        ("[stuff]", "septentrion.ini", {}, True),
        ("[septentrion]\na = b", "septentrion.ini", {"a": "b"}, False),
    ],
)
def test_load_configuration_files_default_files(
    mocker, caplog, conf, filename, expected, has_warning
):
    mocker.patch(
        "septentrion.configuration.read_default_configuration_files",
        return_value=(conf, pathlib.Path(filename).resolve()),
    )
    s = configuration.load_configuration_files(value=None)
    assert s == expected
    warnings = [record for record in caplog.records if record.levelname == "WARNING"]
    assert bool(warnings) is has_warning
    assert all(
        [
            f"/{filename} but contains no septentrion section" in r.message
            for r in warnings
        ]
    )


def test_settings_clean_target_version():
    target = configuration.Settings(target_version="1.2.3").TARGET_VERSION

    assert target == versions.Version(version_tuple=(1, 2, 3), original_string="1.2.3")


def test_settings_clean_schema_version():
    schema = configuration.Settings(schema_version="1.2.3").SCHEMA_VERSION

    assert schema == versions.Version(version_tuple=(1, 2, 3), original_string="1.2.3")
