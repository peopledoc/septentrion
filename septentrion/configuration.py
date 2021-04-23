"""
This is the code around settings loading. For a definition of
the settings, see cli.py (for now)
"""
import configparser
import logging
import pathlib
from typing import Any, Dict, Optional, TextIO, Tuple, Union

from septentrion import exceptions, versions

logger = logging.getLogger(__name__)

# These are the configuration files only used by septentrion
DEDICATED_CONFIGURATION_FILENAME = "septentrion.ini"
CONFIGURATION_PATHS = [
    pathlib.Path("./"),
    pathlib.Path("~/.config/"),
    pathlib.Path("/etc/"),
]
DEDICATED_CONFIGURATION_FILES = [
    folder.expanduser().resolve() / DEDICATED_CONFIGURATION_FILENAME
    for folder in CONFIGURATION_PATHS
]

# These are the files that can contain septentrion configuration, but
# it's also ok if they exist and they don't configure septentrion.
COMMON_CONFIGURATION_FILES = [pathlib.Path("./setup.cfg")]

ALL_CONFIGURATION_FILES = DEDICATED_CONFIGURATION_FILES + COMMON_CONFIGURATION_FILES

DEFAULTS = {
    "create_table": True,
    "table": "septentrion_migrations",
    "version_column": "version",
    "name_column": "name",
    "applied_at_column": "applied_at",
    "migrations_root": ".",
    "schema_template": "schema_{}.sql",
    "fixtures_template": "fixtures_{}.sql",
    "non_transactional_keyword": ["CONCURRENTLY", "ALTER TYPE", "VACUUM"],
    "ignore_symlinks": False,
    "schema_version": None,
    "target_version": None,
    # Values that don't have an explicit default need to be present too
    "verbosity": 0,
    "host": None,
    "port": None,
    "username": None,
    "password": False,
    "dbname": None,
    "additional_schema_file": [],
    "before_schema_file": [],
    "after_schema_file": [],
}


def read_default_configuration_files() -> Tuple[str, pathlib.Path]:
    for file in ALL_CONFIGURATION_FILES:
        try:
            return read_configuration_file(file), file
        except FileNotFoundError:
            logger.info(f"Configuration not found at {file}")
            continue

    logger.info("No configuration file found")
    raise exceptions.NoDefaultConfiguration


def read_configuration_file(path: pathlib.Path) -> str:
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
    def __init__(self, **kwargs):
        self._settings = {}
        self.update(DEFAULTS)
        self.update(kwargs)

    def __getattr__(self, key: str) -> Any:
        try:
            return self._settings[key]
        except KeyError:
            raise AttributeError(key)

    def set(self, key: str, value: Any) -> None:
        upper_key = key.upper()
        lower_key = key.lower()
        try:
            method = getattr(self, f"clean_{lower_key}")
        except AttributeError:
            pass
        else:
            value = method(value)
        self._settings[upper_key] = value

    def clean_migrations_root(
        self, migrations_root: Union[str, pathlib.Path]
    ) -> pathlib.Path:
        if isinstance(migrations_root, str):
            migrations_root = pathlib.Path(migrations_root)
        return migrations_root

    def clean_schema_version(
        self, version: Union[None, str, versions.Version]
    ) -> Optional[versions.Version]:
        if isinstance(version, str):
            version = versions.Version.from_string(version)

        return version

    def clean_target_version(
        self, version: Union[None, str, versions.Version]
    ) -> Optional[versions.Version]:
        if isinstance(version, str):
            version = versions.Version.from_string(version)

        return version

    def __repr__(self):
        return repr(self._settings)

    def update(self, values: Dict) -> None:
        for key, value in values.items():
            self.set(key, value)


def load_configuration_files(value: Optional[TextIO]) -> Dict[str, Any]:
    """
    Load configuration from default source files.
    """
    expected_section = True
    file: Union[pathlib.Path, str]

    if not value:
        try:
            file_contents, file = read_default_configuration_files()
        except exceptions.NoDefaultConfiguration:
            return {}
        if file not in DEDICATED_CONFIGURATION_FILES:
            expected_section = False
    else:
        if hasattr(value, "name"):
            file = pathlib.Path(value.name)
        else:
            file = "stdin"
        logger.info(f"Reading configuration from {file}")

        file_contents = value.read()

    try:
        return parse_configuration_file(file_contents)
    except exceptions.NoSeptentrionSection:
        if expected_section:
            logger.warning(
                f"Configuration file found at {str(file)} but contains no "
                "septentrion section"
            )

    # No configuration found in files ; use stock default values
    return {}
