"""
All things related to the CLI and only that. This module can call functions
from other modules to get the information it needs, then format it and display
it.
"""
import click

from west import __version__
from west import db
from west import migrate
from west import settings
from west import utils
from west import west

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
    "default_map": settings.get_config_settings(),
    "auto_envvar_prefix": "WEST",
    "max_content_width": 120,
}


def print_version(ctx, __, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo("West {}".format(__version__))
    ctx.exit()


def validate_version(ctx, param, value):
    if value and not utils.is_version(value):
        raise click.BadParameter("{value} is not a valid version")
    return value


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="""
    West is a command line tool to manage execution of PostgreSQL
    migrations.
    """,
)
@click.option(
    "--version",
    "-v",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
# @click.option('--log-level',
#               is_flag=True,
#               callback=print_version,
#               expose_value=False,
#               is_eager=True)
@click.option(
    "--host",
    "-H",
    help="Database host (env: PGHOST or WEST_HOST)",
    default="localhost",
    envvar="PGHOST",
)
@click.option(
    "--port",
    "-p",
    help="Database port (env: PGPORT or WEST_PORT)",
    default=5432,
    envvar="PGPORT",
)
@click.option(
    "--username",
    "-U",
    help="Database host (env: PGUSER or WEST_USERNAME)",
    default="postgres",
    envvar="PGUSER",
)
@click.option(
    "--password/--no-password",
    "-W/-w",
    "password_flag",
    help="Prompt for the database password, otherwise read "
    "from environment variable PGPASSWORD, WEST_PASSWORD, "
    "or ~/.pgpass",
    default=False,
    envvar=None,
)
@click.option(
    "--dbname",
    "-d",
    help="Database name (env: PGDATABASE or WEST_DBNAME)",
    default="postgres",
    envvar="PGDATABASE",
)
@click.option(
    "--table",
    help="Database table in which to write migrations " "(env: WEST_TABLE)",
    default="west_migrations",
)
@click.option(
    "--migrations-root",
    help="Path to the migration files " "(env: WEST_MIGRATION_ROOT)",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
)
@click.option(
    "--target-version",
    help="Desired final version of the Database " "(env: WEST_TARGET_VERSION)",
    callback=validate_version,
    required=True,
)
@click.option(
    "--schema-version",
    help="Version of the initial schema (if not "
    "specified, the most resent schema will be used) "
    "(env: WEST_SCHEMA_VERSION)",
    callback=validate_version,
)
@click.option(
    "--schema-template",
    help="Template name for schema files " "(env: WEST_SCHEMA_TEMPLATE)",
    default="schema_{}.sql",
)
@click.option(
    "--fixtures-template",
    help="Template name for schema files " "(env: WEST_FIXTURES_TEMPLATE)",
    default="fixtures_{}.sql",
)
@click.option(
    "--non-transactional-keywords",
    help="When those words are found in the migration, "
    "it is executed outside of a transaction "
    "(comma separated values) "
    "(env: WEST_NON_TRANSACTIONAL_KEYWORDS)",
    default="CONCURRENTLY,ALTER TYPE,VACUUM",
)
@click.option(
    "--additional-schema-files",
    help="Individual sql file names to be run in addition "
    "to the migrations (e.g for installing postgres "
    "extensions) (comma separated paths, relative to "
    "<migration-root>/schemas) "
    "(env: WEST_ADDITIONAL_SCHEMA_FILE)",
)
def cli(**kwargs):
    if kwargs.pop("password_flag"):
        password = click.prompt("Database password:", hide_input=True)
    else:
        password = None
    kwargs["password"] = password

    settings.consolidate(**kwargs)


@click.command()
def show_migrations():
    """
    Show the current state of the database.
    Retrieves informations on the current version
    of the database schema, and the applied and
    unapplied migrations.
    """
    migrations = west.build_migration_plan()
    click.echo("Current version is {}".format(migrations["current_version"]))
    for plan in migrations["plans"]:
        version = plan["version"]
        migrations = plan["plan"]
        click.echo(click.style("Version {}".format(version), bold=True, fg="cyan"))
        for migration in migrations:
            name, applied, path, is_manual = migration
            applied_str, color = ("X", "green") if applied else (" ", "red")
            click.echo(
                "".join(
                    (
                        "  ",
                        click.style(
                            "[{applied}]".format(applied=applied_str), fg=color
                        ),
                        " {}".format(name),
                    )
                )
            )


@click.command()
def init():
    """
    Create the migration table and apply a base schema.
    """
    db.create_table()


@click.command(name="migrate")
def migrate_func():
    """
    Run unapplied migrations up until the most recent one
    """
    migrate.migrate()


cli.add_command(init)
cli.add_command(show_migrations)
cli.add_command(migrate_func)
