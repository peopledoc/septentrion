from septentrion.__main__ import main
from septentrion.db import get_current_schema_version
from septentrion.db import is_schema_initialized


def test_version(cli_runner):
    assert cli_runner.invoke(main, ["--version"]).output == "Septentrion 0.1.4.dev0\n"


def test_current_database_state(cli_runner, db):

    result = cli_runner.invoke(
        main,
        [
            # database connection settings
            "--host",
            db["host"],
            "--port",
            db["port"],
            "--username",
            db["user"],
            "--dbname",
            db["dbname"],
            # migrate settings
            "--target-version",
            "1.1",
            "--migrations-root",
            "example_migrations",
            "migrate",
        ],
    )

    assert result.exit_code == 0
    assert is_schema_initialized()
    assert get_current_schema_version() == "1.1"
