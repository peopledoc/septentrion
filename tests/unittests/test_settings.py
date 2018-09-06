import configparser
import os

from west.settings import get_config_settings


def test_get_config_settings():
    config = configparser.ConfigParser()
    config["west"] = {
        "table": "north_migrations",
    }
    with open("tests/test_west.ini", "w") as configfile:
        config.write(configfile)

    try:
        settings = get_config_settings("tests/test_west.ini")
    finally:
        os.remove("tests/test_west.ini")

    assert settings["table"] == "north_migrations"
