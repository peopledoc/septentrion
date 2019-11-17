import io
import logging

import pytest

from septentrion import runner
from septentrion import settings


def test_clean_sql_code():
    data = """
        SELECT author_data.*
        -- a comment
        \\timing
        FROM author_data;
    """
    expected = "\nSELECT author_data.*\nFROM author_data;\n\n"

    assert runner.clean_sql_code(data) == expected


def test_block_append_line():
    block = runner.Block()
    block.append_line("select true;")

    assert block.content == "select true;"

    block.append_line("commit;")

    assert block.content == "select true;commit;"


def test_block_append_line_closed():
    block = runner.Block()
    block.close()

    with pytest.raises(runner.SQLRunnerException):
        block.append_line("select true")


def test_block_close():
    block = runner.Block()
    block.close()

    assert block.closed is True


def test_block_close_closed():
    block = runner.Block()
    block.close()

    with pytest.raises(runner.SQLRunnerException):
        block.close()


def test_block_run(mocker, caplog):
    caplog.set_level(logging.DEBUG)

    # mock the db cursor
    cursor = mocker.MagicMock(rowcount=1)

    block = runner.Block()
    block.append_line("select true;")
    block.append_line("select false;")

    count = block.run(cursor)

    assert count == 2

    assert caplog.record_tuples == [
        ("septentrion.runner", 10, "Running one statement... <<select true;>>"),
        ("septentrion.runner", 10, "Affected 1 rows"),
        ("septentrion.runner", 10, "Running one statement... <<select false;>>"),
        ("septentrion.runner", 10, "Affected 1 rows"),
    ]


def test_simple_block_run(mocker):
    cursor = mocker.MagicMock()

    block = runner.SimpleBlock()
    block.append_line("select true")
    block.run(cursor)

    cursor.execute.assert_called_with("select true\n")


def test_meta_block_init():
    with pytest.raises(runner.SQLRunnerException):
        runner.MetaBlock("invalid command")


def test_meta_block_run(mocker, caplog):
    caplog.set_level(logging.DEBUG)

    # mock the db cursor
    cursor = mocker.MagicMock(rowcount=0)

    block = runner.MetaBlock("do-until-0")
    block.append_line("select true")
    block.run(cursor)

    assert caplog.record_tuples == [
        ("septentrion.runner", 10, "Running one block in a loop"),
        ("septentrion.runner", 10, "Running one statement... <<select true>>"),
        ("septentrion.runner", 10, "Affected 0 rows"),
        ("septentrion.runner", 10, "Batch delta done : 0"),
    ]


def test_script_manual():
    handler = io.StringIO(
        """
select 1
--meta-psql:do-until-0
-- this is a simple query

select author_data.*
from author_data;

--meta-psql:done
select true;
"""
    )
    handler.name = "/manual/foo.sql"
    settings.consolidate(
        non_transactional_keyword=["CONCURRENTLY", "ALTER TYPE", "VACUUM"], verbose=0
    )
    script = runner.Script(handler)

    b1, b2, b3 = script.block_list

    assert b1.content == "\nselect 1\n"
    assert b2.content == (
        "-- this is a simple query\n\nselect author_data.*\nfrom author_data;\n\n"
    )
    assert b3.content == "select true;\n"
