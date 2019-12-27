import pytest

from septentrion import exceptions, versions


def test_version_constructor():
    version = versions.Version("1.2.3")

    assert version._version == (1, 2, 3)


@pytest.mark.parametrize("version", ["", "a.b.2", "1-2", "1."])
def test_version_bad_string(version):
    with pytest.raises(exceptions.InvalidVersion):
        versions.Version(version)


def test_version_equal():
    assert versions.Version("1.2.3") == versions.Version("1.2.03")


def test_version_not_equal():
    assert versions.Version("1.2.3") != versions.Version("1.2.4")


def test_version_sort():
    version_strings = ["2.2.3", "1.2.7", "4.2.4", "2.2.3", "1.2"]
    version_objs = [versions.Version(s) for s in version_strings]
    assert str(sorted(version_objs)) == (
        '[Version("1.2"), Version("1.2.7"), Version("2.2.3"), Version("2.2.3"), '
        'Version("4.2.4")]'
    )


def test_version_str():
    assert repr(versions.Version("1.2.3")) == 'Version("1.2.3")'


@pytest.mark.parametrize("received,expected", (("1.2.3", "1.2.3"), ("0.01.2", "0.1.2")))
def test_version_normalized_repr(received, expected):
    assert versions.Version(received).normalized_repr() == expected
