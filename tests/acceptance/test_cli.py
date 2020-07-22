from septentrion import __main__, configuration
from septentrion import db as db_module


def test_version(cli_runner):
    assert (
        cli_runner.invoke(__main__.main, ["--version"]).output
        == "septentrion, version 0.0.0\n"
    )


def test_no_configuration_file(cli_runner, temporary_directory, mocker):
    mocker.patch("septentrion.core.describe_migration_plan")
    mocker.patch("septentrion.db.create_table")
    result = cli_runner.invoke(
        __main__.main,
        ["--target-version=0.0.0", "show-migrations"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, (result.output,)


def test_current_database_state(cli_runner, db):
    result = cli_runner.invoke(
        __main__.main,
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
        catch_exceptions=False,
    )
    settings = configuration.Settings(
        host=db["host"], port=db["port"], username=db["user"], dbname=db["dbname"],
    )
    assert result.exit_code == 0
    assert db_module.is_schema_initialized(settings=settings)
    assert (
        db_module.get_current_schema_version(settings=settings).original_string == "1.1"
    )

    assert "Loading schema" in result.output
    assert "Applied 0.1" in result.output
    assert "Version 1.0" in result.output
    assert "Applying 1.0-0-version-dml.sql ..." in result.output
    assert "Applied 1.0-0-version-dml.sql" in result.output
    assert "Version 1.1" in result.output
    assert "Applying 1.1-index-ddl.sql ..." in result.output
    assert "Applied 1.1-index-ddl.sql" in result.output
