"""
This is the code around settings loading. For a definition of
the settings, see cli.py (for now)
"""
import os
import logging


def retrieve_password():
    """
    Extracts password from environment variables
    in consistent priority compared to other
    flags. Note that reading from .pgpass
    will be done by psycopg2 directly
    """
    for envvar in ("PGPASSWORD", "WEST_PASSWORD"):
        if envvar in os.environ:
            return os.environ[envvar]
            break
logger = logging.getLogger(__name__)


def get_config_settings():
    """
    TODO: read configuration file and return
    a dict with values to use if they are
    not overriden in env vars or CLI flags
    """
    return {}


class Settings(object):
    @staticmethod
    def _clean_key(key):
        return key.upper().replace("-", "_")

    def set(self, **kwargs):
        """
        TODO: clean this.
        """
        kwargs = {self._clean_key(key): value for key, value in kwargs.items()}

        vars(self).update(kwargs)


def log_level(verbosity):
    """
    increasing verbosity levels are 0, 1, 2, 3, ...
    corresponding log levels 40, 30, 20, 10
    """
    return 40 - 10 * min(verbosity, 3)


def consolidate(**kwargs):
    settings.set(**kwargs)

    level = log_level(settings.VERBOSE)
    logging.basicConfig(level=level)
    logger.info("Verbosity level: %s", logging.getLevelName(level))


settings = Settings()
