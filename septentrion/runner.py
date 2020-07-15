import logging
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

    def run(self, connection):
        if any("--meta-psql:" in line for line in self.file_lines):
            self._run_with_meta_loop()
        else:
            self._run_simple()

    def _run_simple(self):
        try:
            # FIXME: handle PG credentials & DB
            cmd = subprocess.run(
                ["psql", "--set", "ON_ERROR_STOP=on", "-f", self.path],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise SQLRunnerException('Error during migration') from e

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
