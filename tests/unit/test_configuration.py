import pytest

from septentrion import configuration, exceptions


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


def test_settings_from_cli():
    s = configuration.Settings.from_cli({"foo": "blah"})

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
