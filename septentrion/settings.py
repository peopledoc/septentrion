"""
This is the code around settings loading. For a definition of
the settings, see cli.py (for now)
"""
import configparser
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def get_config_settings(content: str) -> Dict:
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

    logger.warning(
        "Found a config file but there isn't any 'septentrion' section in it"
    )
    return {}


class Settings(dict):
    def __getattr__(self, key: str) -> Any:
        return self[key]

    @staticmethod
    def _clean_key(key: str) -> str:
        return key.upper()

    def set(self, **kwargs) -> None:
        """
        TODO: clean this.
        """
        self.update({self._clean_key(key): value for key, value in kwargs.items()})


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


def consolidate(**kwargs) -> None:
    settings.set(**kwargs)

    level = log_level(settings.VERBOSE)
    logging.basicConfig(level=level)
    logger.info("Verbosity level: %s", logging.getLevelName(level))


settings = Settings()
