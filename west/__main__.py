import click

CONTEXT_SETTINGS = {'help_option_names': ['-h', '--help']}


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


@click.command()
def show_migrations():
    click.echo("1.2.3")


main.add_command(show_migrations)


if __name__ == '__main__':
    main()
