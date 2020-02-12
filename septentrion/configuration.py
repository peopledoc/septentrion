"""
This is the code around settings loading. For a definition of
the settings, see cli.py (for now)
"""
import configparser
import logging
import pathlib
from typing import Any, Dict, Tuple, Union

from septentrion import exceptions

logger = logging.getLogger(__name__)

# These are the configuration files only used by septentrion
DEDICATED_CONFIGURATION_FILES = [
    "./septentrion.ini",
    "~/.config/septentrion.ini",
    "/etc/septentrion.ini",
]
# These are the files that can contain septentrion configuration, but
# it's also ok if they exist and they don't configure septentrion.
COMMON_CONFIGURATION_FILES = ["./setup.cfg"]

ALL_CONFIGURATION_FILES = DEDICATED_CONFIGURATION_FILES + COMMON_CONFIGURATION_FILES

DEFAULTS = {
    "table": "septentrion_migrations",
    "migrations_root": ".",
    "schema_template": "schema_{}.sql",
    "fixtures_template": "fixtures_{}.sql",
    "non_transactional_keyword": ["CONCURRENTLY", "ALTER TYPE", "VACUUM"],
    "ignore_symlinks": False,
    # Values that don't have an explicit default need to be present too
    "verbosity": 0,
    "host": None,
    "port": None,
    "username": None,
    "password": False,
    "dbname": None,
    "schema_version": None,
    "additional_schema_file": [],
    "before_schema_file": [],
    "after_schema_file": [],
}


def read_default_configuration_files() -> Tuple[str, str]:
    for file in ALL_CONFIGURATION_FILES:
        try:
            return read_configuration_file(file), file
        except FileNotFoundError:
            logger.info(f"Configuration not found at {file}")
            continue

    logger.info("No configuration file found")
    raise exceptions.NoDefaultConfiguration


def read_configuration_file(path: str) -> str:
    with open(path, "r") as handler:
        logger.info(f"Reading configuration from {path}")
        return handler.read()


def parse_configuration_file(content: str) -> Dict:
    """
    Read configuration file and return
    a dict with values to use if they are
    not overwritten in env vars or CLI flags
    """
    parser = configparser.ConfigParser()
    parser.read_string(content)

    if "septentrion" in parser:
        config: Dict[str, Any] = dict(parser["septentrion"])
        if "additional_schema_file" in config:
            config["additional_schema_file"] = [
                line for line in config["additional_schema_file"].splitlines() if line
            ]

        if "before_schema_file" in config:
            config["before_schema_file"] = [
                line for line in config["before_schema_file"].splitlines() if line
            ]

        if "after_schema_file" in config:
            config["after_schema_file"] = [
                line for line in config["after_schema_file"].splitlines() if line
            ]

        return config

    raise exceptions.NoSeptentrionSection


def log_level(verbosity: int) -> int:
    """
    verbosity  | log level
    (input)    | (output)
    -----------|-------------
    0 ("")     | 40 (ERROR)
    1 ("-v")   | 30 (WARNING)
    2 ("-vv")  | 20 (INFO)
    3 ("-vvv") | 10 (DEBUG)
    """
    return 40 - 10 * min(verbosity, 3)


class Settings:
    def __init__(self):
        self._settings = {}
        self.update(DEFAULTS)

    def __getattr__(self, key: str) -> Any:
        try:
            return self._settings[key]
        except KeyError:
            raise AttributeError(key)

    def set(self, key: str, value: Any) -> None:
        try:
            method = getattr(self, f"clean_{key.lower()}")
        except AttributeError:
            pass
        else:
            value = method(value)
        # TODO: remove the .upper() and fix the tests: from_cli() should be
        # the only one doing the .upper()
        self._settings[key.upper()] = value

    def clean_migrations_root(
        self, migrations_root: Union[str, pathlib.Path]
    ) -> pathlib.Path:
        if isinstance(migrations_root, str):
            migrations_root = pathlib.Path(migrations_root)
        return migrations_root

    def __repr__(self):
        return repr(self._settings)

    def update(self, values: Dict) -> None:
        for key, value in values.items():
            self.set(key, value)

    @classmethod
    def from_cli(cls, cli_settings: Dict):
        settings = cls()
        # CLI settings are lowercase
        settings.update({key.upper(): value for key, value in cli_settings.items()})

        return settings
