import logging

import pytest
from west import settings


def test_get_config_settings():
    config = """
        [west]
        table = north_migrations
    """
    s = settings.get_config_settings(config)

    assert s == {"table": "north_migrations"}


def test_get_config_settings_no_section(caplog):
    config = """
        [east]
        table = north_migrations
    """
    s = settings.get_config_settings(config)

    assert s == {}
    assert caplog.records[0].message == (
        "Found a config file but there isn't any 'west' section in it"
    )


def test_settings():
    s = settings.Settings()
    s.set(foo="blah")

    assert s.FOO == "blah"


@pytest.mark.parametrize("verbosity,expected", [(0, 40), (3, 10), (4, 10)])
def test_log_level(verbosity, expected):
    assert settings.log_level(verbosity) == expected


def test_consolidate(caplog, mocker):
    caplog.set_level(logging.DEBUG)
    mock = mocker.patch("logging.basicConfig")

    settings.consolidate(foo="blah", verbose=3)

    assert settings.settings.FOO == "blah"
    assert caplog.records[0].message == "Verbosity level: DEBUG"
    mock.assert_called_with(level=10)
