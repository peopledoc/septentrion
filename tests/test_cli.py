def test_version(click):
    assert click.run("--version").stdout == "0.1.0"

