import septentrion
from septentrion import configuration
from septentrion import db as db_module


def test_migrate(db):

    settings_kwargs = {
        # database connection settings
        "host": db["host"],
        "port": db["port"],
        "username": db["user"],
        "dbname": db["dbname"],
        # migrate settings
        "target_version": "1.1",
        "migrations_root": "example_migrations",
    }

    septentrion.migrate(**settings_kwargs)

    settings = configuration.Settings(**settings_kwargs)
    assert db_module.is_schema_initialized(settings=settings)
    assert (
        db_module.get_current_schema_version(settings=settings).original_string == "1.1"
    )
