import click

from west import db
from west import settings
# from west import migrations

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@click.command()
def show_migrations():
    # click.echo(migrations.list_migrations_files(settings))
    click.echo(db.get_applied_migrations(settings))
    click.echo(db.get_schema_version(settings))


@click.command()
def init():
    db.create_table(settings)


@click.command()
def migrate():
    db.write_migration(settings, "18.3", "youpi.sql")


main.add_command(init)
main.add_command(show_migrations)
main.add_command(migrate)


if __name__ == '__main__':
    main()
