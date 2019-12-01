"""
This is the code around settings loading. For a definition of
the settings, see cli.py (for now)
"""
import configparser
import logging
from typing import Any, Dict, Tuple

from septentrion import exceptions

logger = logging.getLogger(__name__)

# These are the dedicated septentrion configuration files
CONFIGURATION_FILES = [
    "./septentrion.ini",
    "~/.config/septentrion.ini",
    "/etc/septentrion.ini",
]
# These are the files that can contain septentrion configuration, but
# it's also ok if they exist and they don't configure septentrion.
COMMON_CONFIGURATION_FILES = ["./setup.cfg"]

ALL_CONFIGURATION_FILES = CONFIGURATION_FILES + COMMON_CONFIGURATION_FILES


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


def clean_key(key: str) -> str:
    return key.upper()


class Settings:
    def __init__(self):
        self._settings = {}

    def __getattr__(self, key: str) -> Any:
        return self._settings[key]

    def set(self, key: str, value: Any) -> None:
        self._settings[clean_key(key)] = value

    def __repr__(self):
        return repr(self._settings)

    @classmethod
    def from_cli(cls, cli_settings: Dict):
        # CLI settings are lowercase
        settings = cls()
        for key, value in cli_settings.items():
            settings.set(key, value)

        return settings
