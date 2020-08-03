import io
import os

import pytest

from septentrion.db import Query
from septentrion.runner import Script, SQLRunnerException


@pytest.fixture()
def run_script(db, settings_factory, tmp_path):
    settings = settings_factory(**db)

    def _run_script(script):
        path = tmp_path / "script.sql"
        path.write_text(script)

        with io.open(path, "r", encoding="utf8") as f:
            script = Script(settings, f, path)
            script.run()

    return _run_script


@pytest.fixture()
def env():
    environ = {**os.environ}
    yield os.environ
    os.environ.clear()
    os.environ.update(environ)


def test_run_simple(db, settings_factory, run_script):
    settings = settings_factory(**db)

    run_script("CREATE TABLE foo ();")

    query = "SELECT COUNT(*) FROM pg_catalog.pg_tables WHERE tablename = 'foo'"
    with Query(settings, query) as cur:
        assert [row[0] for row in cur] == [1]


def test_run_simple_error(run_script):
    with pytest.raises(SQLRunnerException) as err:
        run_script("CREATE TABLE ???")

    assert 'ERROR:  syntax error at or near "???"' in str(err.value)


def test_run_psql_not_found(run_script, env):
    env["PATH"] = ""

    with pytest.raises(RuntimeError) as err:
        run_script("SELECT 1;")

    assert str(err.value) == (
        "Septentrion requires the 'psql' executable to be present in the PATH."
    )


def test_run_integer_in_settings(db, settings_factory, env, tmp_path):
    settings = settings_factory(**db)
    # settings are noew stringified to prevent subprocess.run
    # crashing while building the appropriate command line.
    settings.PORT = 5432
    path = tmp_path / "script.sql"
    path.write_text("SELECT 1;")
    with io.open(path, "r", encoding="utf8") as f:
        script = Script(settings, f, path)
        script.run()


def test_run_with_meta_loop(db, settings_factory, run_script):
    settings = settings_factory(**db)

    # create a table with 10 rows
    script = """
CREATE TABLE foo(value int);
INSERT INTO foo SELECT generate_series(1, 10);
    """
    run_script(script)

    query = "SELECT * FROM foo ORDER BY value"
    with Query(settings, query) as cur:
        assert [row[0] for row in cur] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # update the rows 3 by 3 to multiply them by 100
    script = """
--meta-psql:do-until-0
WITH to_update AS (
    SELECT value FROM foo WHERE value < 100 LIMIT 3
)
UPDATE foo SET value = foo.value * 100
  FROM to_update WHERE foo.value = to_update.value
--meta-psql:done
    """
    run_script(script)

    query = "SELECT * FROM foo ORDER BY value"
    with Query(settings, query) as cur:
        assert [row[0] for row in cur] == [
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800,
            900,
            1000,
        ]
