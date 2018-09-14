from west.settings import get_config_settings


def test_get_config_settings():
    config = """
        [west]
        table = north_migrations
    """
    settings = get_config_settings(config)

    assert settings == {
        "table": "north_migrations"
    }


def test_get_config_settings_no_section(caplog):
    config = """
        [east]
        table = north_migrations
    """
    settings = get_config_settings(config)
    assert settings == {}
    assert caplog.records[0].message == ("Found a config file but there "
                                         "isn't any 'west' section in it")
