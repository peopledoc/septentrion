from west.__main__ import main


def test_current_database_state(cli_runner):

    result = cli_runner.invoke(main, ["show_migrations"])

    assert result.exit_code == 0
    assert result.output == '1.2.3'
