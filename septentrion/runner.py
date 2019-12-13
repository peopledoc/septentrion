import logging
import pathlib
from typing import Iterable

import sqlparse
from psycopg2.extensions import cursor as Cursor

from septentrion import configuration, files

logger = logging.getLogger(__name__)


class SQLRunnerException(Exception):
    pass


def clean_sql_code(code: str) -> str:
    output = ""
    for line in code.split("\n"):
        stripped_line = line.strip()
        if stripped_line == "\\timing":
            continue
        if stripped_line.startswith("--"):
            continue
        output += stripped_line + "\n"
    return output


class Block(object):
    def __init__(self):
        self.closed = False
        self.content = ""

    def append_line(self, line: str) -> None:
        if self.closed:
            raise SQLRunnerException("Block closed !")
        self.content += line

    def close(self) -> None:
        if self.closed:
            raise SQLRunnerException("Block closed !")
        self.closed = True

    def run(self, cursor: Cursor) -> int:
        statements = sqlparse.parse(self.content)

        content = "".join(str(stmt) for stmt in statements)
        if content != self.content:
            raise SQLRunnerException("sqlparse failed to properly split input")

        rows = 0
        for statement in statements:
            if clean_sql_code(str(statement)).strip() in ("", ";"):
                # Sometimes sqlparse keeps the empty lines here,
                # this could negatively affect libpq
                continue
            logger.debug("Running one statement... <<%s>>", str(statement))
            cursor.execute(str(statement).replace("\\timing\n", ""))
            logger.debug("Affected %s rows", cursor.rowcount)
            rows += cursor.rowcount
        return rows


class SimpleBlock(Block):
    def run(self, cursor):
        statements = clean_sql_code(self.content)
        cursor.execute(statements)


class MetaBlock(Block):
    def __init__(self, command: str):
        super(MetaBlock, self).__init__()
        self.command = command
        if command != "do-until-0":
            raise SQLRunnerException("Unexpected command {}".format(command))

    def run(self, cursor: Cursor) -> int:
        total_rows = 0
        # Simply call super().run in a loop...
        delta = 0
        batch_delta = -1
        while batch_delta != 0:
            batch_delta = 0
            logger.debug("Running one block in a loop")
            delta = super(MetaBlock, self).run(cursor)
            if delta > 0:
                total_rows += delta
                batch_delta = delta
            logger.debug("Batch delta done : %s", batch_delta)
        return total_rows


class Script(object):
    def __init__(
        self,
        settings: configuration.Settings,
        file_handler: Iterable[str],
        path: pathlib.Path,
    ):
        file_lines = list(file_handler)
        is_manual = files.is_manual_migration(
            migration_path=path, migration_contents=file_lines
        )
        self.settings = settings
        if is_manual:
            self.block_list = [Block()]
        elif self.contains_non_transactional_keyword(file_lines):
            self.block_list = [Block()]
        else:
            self.block_list = [SimpleBlock()]
        for line in file_lines:
            if line.startswith("--meta-psql:") and is_manual:
                self.block_list[-1].close()
                command = line.split(":")[1].strip()
                if command == "done":
                    # create a new basic block
                    self.block_list.append(Block())
                else:
                    # create a new meta block
                    self.block_list.append(MetaBlock(command))
            else:
                self.block_list[-1].append_line(line)
        self.block_list[-1].close()

    def run(self, connection):
        with connection.cursor() as cursor:
            for block in self.block_list:
                block.run(cursor)

    def contains_non_transactional_keyword(self, file_lines: Iterable[str]) -> bool:
        keywords = self.settings.NON_TRANSACTIONAL_KEYWORD
        for line in file_lines:
            for kw in keywords:
                if kw.lower() in line.lower():
                    return True

        return False
