from west.__main__ import main
from west.db import get_schema_version


def test_version(cli_runner):
    assert cli_runner.invoke(main, ["--version"]).output == "0.1.0"


def test_current_database_state(cli_runner):

    result = cli_runner.invoke(main, ["show_migrations"])

    assert result.exit_code == 0
    assert result.output == '{}\n'.format(get_schema_version())
