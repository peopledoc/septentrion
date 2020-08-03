import logging
import os
import pathlib
import subprocess
from typing import Iterable

from septentrion import configuration

logger = logging.getLogger(__name__)


class SQLRunnerException(Exception):
    pass


class Script:
    def __init__(
        self,
        settings: configuration.Settings,
        file_handler: Iterable[str],
        path: pathlib.Path,
    ):
        self.settings = settings
        self.file_lines = list(file_handler)
        self.path = path

    def run(self):
        if any("--meta-psql:" in line for line in self.file_lines):
            self._run_with_meta_loop()
        else:
            self._run_simple()

    def _env(self):
        environment = {
            "PGHOST": self.settings.HOST,
            "PGPORT": self.settings.PORT,
            "PGDATABASE": self.settings.DBNAME,
            "PGUSER": self.settings.USERNAME,
            "PGPASSWORD": self.settings.PASSWORD,
        }
        return {key: str(value) for key, value in environment.items() if value}

    def _run_simple(self):

        try:
            cmd = subprocess.run(
                ["psql", "--set", "ON_ERROR_STOP=on", "-f", str(self.path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                # environment has precedence over os.environ
                env={**os.environ, **self._env()},
            )
        except FileNotFoundError:
            raise RuntimeError(
                "Septentrion requires the 'psql' executable to be present in "
                "the PATH."
            )
        except subprocess.CalledProcessError as e:
            msg = "Error during migration: {}".format(e.stderr.decode("utf-8"))
            raise SQLRunnerException(msg) from e

        return cmd.stdout.decode("utf-8")

    def _run_with_meta_loop(self):
        KEYWORDS = ["INSERT", "UPDATE", "DELETE"]
        rows_remaining = True

        while rows_remaining:
            out = self._run_simple()

            # we can stop once all the write operations return 0 rows
            for line in out.split("\n"):
                rows_remaining = any(
                    keyword in line and keyword + " 0" not in line
                    for keyword in KEYWORDS
                )

                # we still have work to do, we can go back to the main loop
                if rows_remaining:
                    break
