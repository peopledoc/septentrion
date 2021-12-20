import pytest

from septentrion.utils import is_version, until


@pytest.mark.parametrize("value,expected", [("1.2", True), ("bananas", False)])
def test_is_version(value, expected):
    assert is_version(value) == expected


def test_until():
    values = list(until(range(300), 3))

    assert values == [0, 1, 2, 3]


def test_until_error():
    with pytest.raises(ValueError):
        list(until(range(5), 10))


def test_since():
    values = list(until(range(300), 297))

    assert values == [297, 298, 299]
