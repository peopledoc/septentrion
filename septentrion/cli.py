"""
All things related to the CLI and only that. This module can call functions
from other modules to get the information it needs, then format it and display
it.
"""
import functools
import logging
import os
from typing import Any, TextIO

import click
from click.types import StringParamType

from septentrion import (
    __version__,
    configuration,
    core,
    exceptions,
    migration,
    style,
    versions,
)

logger = logging.getLogger(__name__)


# By default, click options don't show their default value, except if we pass
# `show_default=True`. We could pass show_default in the context, but then we would not
# be able to disable it for a single option, as stated in the doc:
# https://click.palletsprojects.com/en/7.x/api/?highlight=show_default#context
# So we modify the click.option callable and change the default value of the argument.
# (From https://github.com/pallets/click/issues/1018#issuecomment-416969437)
click.option = functools.partial(click.option, show_default=True)  # type: ignore


def load_config(ctx: click.Context, param: click.Parameter, value: TextIO) -> None:
    ctx.default_map = configuration.load_configuration_files(value)


CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "auto_envvar_prefix": "SEPTENTRION",
    "max_content_width": 120,
}

LATEST_VERSION = "latest"


def validate_version(ctx: click.Context, param: Any, value: str):
    if value == LATEST_VERSION:
        return None
    try:
        version = versions.Version.from_string(value)
    except exceptions.InvalidVersion:
        raise click.BadParameter(f"{value} is not a valid version")
    return version


class CommaSeparatedMultipleString(StringParamType):
    envvar_list_splitter = ","

    def split_envvar_value(self, rv: str):
        values = super(CommaSeparatedMultipleString, self).split_envvar_value(rv)
        return tuple(value.strip() for value in values)


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="""
    Septentrion is a command line tool to manage execution of PostgreSQL
    migrations. It uses a migration table to synchronize migration
    execution.
    """,
)
@click.pass_context
@click.option(
    "--config-file",
    is_eager=True,
    callback=load_config,
    help="Config file to use (env: SEPTENTRION_CONFIG_FILE)  "
    f"[default: {' or '.join(str(p) for p in configuration.ALL_CONFIGURATION_FILES)}]",
    type=click.File("r"),
)
@click.version_option(__version__, "-V", "--version", prog_name="septentrion")
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    show_default=False,
    help="Raises verbosity level (can be used multiple times)"
    "(env: SEPTENTRION_VERBOSITY, int)",
)
@click.option("--host", "-H", help="Database host (env: SEPTENTRION_HOST or PGHOST)")
@click.option("--port", "-p", help="Database port (env: SEPTENTRION_PORT or PGPORT)")
@click.option(
    "--username", "-U", help="Database host (env: SEPTENTRION_USERNAME or PGUSER)"
)
@click.option(
    "--password/--no-password",
    "-W/-w",
    "password_flag",
    help="Prompt for the database password, otherwise read from environment variable "
    "PGPASSWORD, SEPTENTRION_PASSWORD, or ~/.pgpass",
    envvar=None,
)
@click.option(
    "--dbname", "-d", help="Database name (env: SEPTENTRION_DBNAME or PGDATABASE)"
)
@click.option(
    "--table",
    help="Database table in which to write migrations. The table will be created "
    "immediately if it doesn't exist (env: SEPTENTRION_TABLE)",
    default=configuration.DEFAULTS["table"],
)
@click.option(
    "--version_column",
    help="Name of the column describing the migration version in the migrations table. "
    "(env: SEPTENTRION_VERSION_COLUMN)",
    default=configuration.DEFAULTS["version_column"],
)
@click.option(
    "--name_column",
    help="Name of the column describing the migration name in the migrations table. "
    "(env: SEPTENTRION_NAME_COLUMN)",
    default=configuration.DEFAULTS["name_column"],
)
@click.option(
    "--applied_at_column",
    help="Name of the column describing the date at which the migration was applied "
    "in the migrations table. (env: SEPTENTRION_APPLIED_AT_COLUMN)",
    default=configuration.DEFAULTS["applied_at_column"],
)
@click.option(
    "--migrations-root",
    help="Path to the migration files (env: SEPTENTRION_MIGRATION_ROOT)",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=configuration.DEFAULTS["migrations_root"],
)
@click.option(
    "--target-version",
    help="Desired final version of the Database (env: SEPTENTRION_TARGET_VERSION)",
    default=LATEST_VERSION,
    callback=validate_version,
)
@click.option(
    "--schema-version",
    help="Version of the initial schema (if not specified, the most recent schema "
    "will be used) (env: SEPTENTRION_SCHEMA_VERSION)",
    default=LATEST_VERSION,
    callback=validate_version,
)
@click.option(
    "--schema-template",
    help="Template name for schema files " "(env: SEPTENTRION_SCHEMA_TEMPLATE)",
    default=configuration.DEFAULTS["schema_template"],
)
@click.option(
    "--fixtures-template",
    help="Template name for fixtures files " "(env: SEPTENTRION_FIXTURES_TEMPLATE)",
    default=configuration.DEFAULTS["fixtures_template"],
)
@click.option(
    "--non-transactional-keyword",
    multiple=True,
    type=CommaSeparatedMultipleString(),
    help="When those words are found in the migration, it is executed outside of a "
    "transaction (repeat the flag as many times as necessary) "
    "(env: SEPTENTRION_NON_TRANSACTIONAL_KEYWORD, comma separated values)",
    default=configuration.DEFAULTS["non_transactional_keyword"],
)
@click.option(
    "--additional-schema-file",
    multiple=True,
    type=CommaSeparatedMultipleString(),
    help="Path to a SQL file relative to <migration-root>/schemas, to be run in "
    "addition to the migrations, e.g for installing postgres extensions (repeat the "
    "flag as many times as necessary) (env: SEPTENTRION_ADDITIONAL_SCHEMA_FILE, comma "
    "separated values) DEPRECATED; please use --before-schema-file",
)
@click.option(
    "--before-schema-file",
    multiple=True,
    type=CommaSeparatedMultipleString(),
    help="Path to a SQL file relative to <migration-root>/schemas, to be run in "
    "addition to the migrations, before the main schemas, e.g for installing postgres "
    "extensions (repeat the flag as many times as necessary) (env: "
    "SEPTENTRION_BEFORE_SCHEMA_FILE, comma separated values)",
)
@click.option(
    "--after-schema-file",
    multiple=True,
    type=CommaSeparatedMultipleString(),
    help="Path to a SQL file relative to <migration-root>/schemas, to be run in "
    "addition to the migrations, after the main schemas, e.g for grant files "
    "(repeat the flag as many times as necessary) (env: SEPTENTRION_AFTER_SCHEMA_FILE, "
    "comma separated values)",
)
@click.option(
    "--ignore-symlinks/--no-ignore-symlinks",
    default=configuration.DEFAULTS["ignore_symlinks"],
    help="Ignore migration files that are symlinks",
)
@click.option(
    "--create-table/--no-create-table",
    default=configuration.DEFAULTS["create_table"],
    help="Controls whether the migrations table should be created if it doesn't exist. "
    "(env: SEPTENTRION_CREATE_TABLE)",
)
def cli(ctx: click.Context, **kwargs):
    if kwargs.pop("password_flag"):
        password = click.prompt("Database password", hide_input=True)
    else:
        password = os.getenv("SEPTENTRION_PASSWORD")
    kwargs["password"] = password

    ctx.obj = settings = core.initialize(**kwargs)

    level = configuration.log_level(verbosity=settings.VERBOSITY)
    logging.basicConfig(level=level)
    logger.info("Verbosity level: %s", logging.getLevelName(level))


@cli.command(name="show-migrations")
@click.pass_obj
def show_migrations(settings: configuration.Settings):
    """
    Show the current state of the database.
    Retrieves informations on the current version
    of the database schema, and the applied and
    unapplied migrations.
    """
    core.describe_migration_plan(settings=settings, stylist=style.stylist)


@cli.command()
@click.pass_obj
def migrate(settings: configuration.Settings):
    """
    Run unapplied migrations.
    """
    migration.migrate(settings=settings, stylist=style.stylist)


@cli.command()
@click.argument("version", callback=validate_version)
@click.pass_obj
def fake(settings: configuration.Settings, version: versions.Version):
    """
    Fake migrations until version.
    Write migrations in the migration table without applying them, for
    all migrations up until the given version (included). This is useful
    when installing septentrion on an existing DB.
    """
    migration.create_fake_entries(settings=settings, version=version)
