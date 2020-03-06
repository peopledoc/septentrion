import pytest

from septentrion import lib, style, versions


@pytest.mark.parametrize(
    "kwargs, stylist",
    [
        ({"quiet": True}, style.noop_stylist),
        ({"quiet": False}, style.stylist),
        ({}, style.stylist),
    ],
)
def test_lib_kwargs_stylist(kwargs, stylist):
    assert lib.lib_kwargs(kwargs)["stylist"] is stylist


def test_lib_kwargs_settings():
    assert lib.lib_kwargs({"a": 1})["settings"].A == 1


def test_lib_kwargs():
    assert sorted(lib.lib_kwargs({})) == ["settings", "stylist"]


def test_migrate(mocker):
    mock = mocker.patch("septentrion.migration.migrate")
    callback = mocker.Mock()
    lib.migrate(migration_applied_callback=callback)

    mock.assert_called_with(
        migration_applied_callback=callback, settings=mocker.ANY, stylist=mocker.ANY
    )


def test_fake(mocker):
    mock = mocker.patch("septentrion.migration.create_fake_entries")

    lib.fake(version="1.2.3")

    mock.assert_called_with(version=mocker.ANY, settings=mocker.ANY, stylist=mocker.ANY)
    _, k = mock.call_args
    assert k["version"] == versions.Version((1, 2, 3), "1.2.3")


def test_show_migrations(mocker):
    mock = mocker.patch("septentrion.core.describe_migration_plan")

    lib.show_migrations()

    mock.assert_called_with(settings=mocker.ANY, stylist=mocker.ANY)
