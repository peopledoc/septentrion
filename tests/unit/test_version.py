import pytest

from septentrion import exceptions, versions


def test_version_constructor():
    version = versions.Version.from_string("1.2.3")

    assert version.version_tuple == (1, 2, 3)


@pytest.mark.parametrize("version", ["", "a.b.2", "1-2", "1."])
def test_version_bad_string(version):
    with pytest.raises(exceptions.InvalidVersion):
        versions.Version.from_string(version)


def test_version_equal():
    assert versions.Version.from_string("1.2.3") == versions.Version.from_string(
        "1.2.03"
    )


def test_version_not_equal():
    assert versions.Version.from_string("1.2.3") != versions.Version.from_string(
        "1.2.4"
    )


def test_version_sort():
    version_strings = ["2.2.3", "1.2.7", "4.2.4", "2.2.3", "1.2"]
    version_objs = [versions.Version.from_string(s) for s in version_strings]
    assert [v.original_string for v in sorted(version_objs)] == [
        "1.2",
        "1.2.7",
        "2.2.3",
        "2.2.3",
        "4.2.4",
    ]


def test_version_repr():
    assert (
        repr(versions.Version.from_string("1.2.3"))
        == "Version(version_tuple=(1, 2, 3), original_string='1.2.3')"
    )


def test_version_str():
    assert str(versions.Version.from_string("1.2.3")) == "1.2.3"

    assert str(versions.Version.from_string("1.2.03")) == "1.2.03"
