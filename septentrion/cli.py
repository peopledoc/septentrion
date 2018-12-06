"""
All things related to the CLI and only that. This module can call functions
from other modules to get the information it needs, then format it and display
it.
"""
import logging
import os

import click
from click.types import StringParamType

from septentrion import __version__
from septentrion import core
from septentrion import db
from septentrion import migrate
from septentrion import settings
from septentrion import style
from septentrion import utils

logger = logging.getLogger(__name__)


def get_context_settings():
    try:
        with open("septentrion.ini") as file:
            config = file.read()
    except FileNotFoundError:
        config = ""

    return {
        "help_option_names": ["-h", "--help"],
        "default_map": settings.get_config_settings(config),
        "auto_envvar_prefix": "SEPTENTRION",
        "max_content_width": 120,
    }


CONTEXT_SETTINGS = get_context_settings()


def print_version(ctx, __, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("Septentrion {}".format(__version__))
    ctx.exit()


def validate_version(ctx, param, value):
    if value and not utils.is_version(value):
        raise click.BadParameter("{value} is not a valid version")
    return value


class CommaSeparatedMultipleString(StringParamType):
    envvar_list_splitter = ","

    def split_envvar_value(self, rv):
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
@click.option(
    "-V",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
@click.option("-v", "--verbose", count=True)
@click.option(
    "--host",
    "-H",
    help="Database host (env: SEPTENTRION_HOST or PGHOST)",
    show_default=True,
    default="localhost",
)
@click.option(
    "--port",
    "-p",
    help="Database port (env: SEPTENTRION_PORT or PGPORT)",
    show_default=True,
    default=5432,
)
@click.option(
    "--username",
    "-U",
    help="Database host (env: SEPTENTRION_USERNAME or PGUSER)",
    show_default=True,
    default="postgres",
)
@click.option(
    "--password/--no-password",
    "-W/-w",
    "password_flag",
    help="Prompt for the database password, otherwise read from environment variable "
    "PGPASSWORD, SEPTENTRION_PASSWORD, or ~/.pgpass",
    show_default=True,
    default=False,
    envvar=None,
)
@click.option(
    "--dbname",
    "-d",
    help="Database name (env: SEPTENTRION_DBNAME or PGDATABASE)",
    show_default=True,
    default="postgres",
)
@click.option(
    "--table",
    help="Database table in which to write migrations. The table will be created"
    "immediately if it doesn't exist (env: SEPTENTRION_TABLE)",
    show_default=True,
    default="septentrion_migrations",
)
@click.option(
    "--migrations-root",
    help="Path to the migration files (env: SEPTENTRION_MIGRATION_ROOT)",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    show_default=True,
    default=".",
)
@click.option(
    "--target-version",
    help="Desired final version of the Database (env: SEPTENTRION_TARGET_VERSION)",
    callback=validate_version,
    required=True,
)
@click.option(
    "--schema-version",
    help="Version of the initial schema (if not specified, the most resent schema "
    "will be used) (env: SEPTENTRION_SCHEMA_VERSION)",
    callback=validate_version,
)
@click.option(
    "--schema-template",
    help="Template name for schema files " "(env: SEPTENTRION_SCHEMA_TEMPLATE)",
    show_default=True,
    default="schema_{}.sql",
)
@click.option(
    "--fixtures-template",
    help="Template name for schema files " "(env: SEPTENTRION_FIXTURES_TEMPLATE)",
    show_default=True,
    default="fixtures_{}.sql",
)
@click.option(
    "--non-transactional-keyword",
    multiple=True,
    show_default=True,
    type=CommaSeparatedMultipleString(),
    help="When those words are found in the migration, it is executed outside of a "
    "transaction (repeat the flag as many times as necessary) "
    "(env: SEPTENTRION_NON_TRANSACTIONAL_KEYWORD, comma separated values)",
    default=["CONCURRENTLY", "ALTER TYPE", "VACUUM"],
)
@click.option(
    "--additional-schema-file",
    multiple=True,
    type=CommaSeparatedMultipleString(),
    help="Path to a SQL file relative to <migration-root>/schemas, to be run in "
    "addition to the migrations, e.g for installing postgres extensions (repeat the "
    "flag as many times as necessary) (env: SEPTENTRION_ADDITIONAL_SCHEMA_FILE, comma "
    "separated values)",
)
def cli(**kwargs):
    if kwargs.pop("password_flag"):
        password = click.prompt("Database password", hide_input=True)
    else:
        password = os.getenv("SEPTENTRION_PASSWORD")
    kwargs["password"] = password

    settings.consolidate(**kwargs)

    # All other commands will need to table to be created
    logger.info("Ensuring migration table exists")
    # TODO: this probably deserves an option
    db.create_table()  # idempotent


@cli.command(name="show-migrations")
def show_migrations():
    """
    Show the current state of the database.
    Retrieves informations on the current version
    of the database schema, and the applied and
    unapplied migrations.
    """
    core.describe_migration_plan(stylist=style.stylist)


@cli.command(name="migrate")
def migrate_func():
    """
    Run unapplied migrations.

    """
    migrate.migrate(stylist=style.stylist)


@cli.command()
@click.argument("version", callback=validate_version)
def fake(version):
    """
    Fake migrations until version.
    Write migrations in the migration table without applying them, for
    all migrations up until the given version (included). This is useful
    when installing septentrion on an existing DB.
    """
    migrate.create_fake_entries(version)
