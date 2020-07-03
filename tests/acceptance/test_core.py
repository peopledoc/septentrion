from septentrion import core


def test_initialize(db):

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

    # create table with no error
    core.initialize(**settings_kwargs)
    # action is idempotent, no error either
    core.initialize(**settings_kwargs)


def test_initialize_customize_names(db):

    settings_kwargs = {
        # database connection settings
        "host": db["host"],
        "port": db["port"],
        "username": db["user"],
        "dbname": db["dbname"],
        # migrate settings
        "target_version": "1.1",
        "migrations_root": "example_migrations",
        # customize table
        "table": "my_own_table",
        # customize columns
        "name_column": "name_custo",
        "version_column": "version_custo",
        "applied_at_column": "applied_custo",
    }

    # create table with no error
    core.initialize(**settings_kwargs)
    # action is idempotent, no error either
    core.initialize(**settings_kwargs)
