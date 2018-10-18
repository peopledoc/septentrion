import pytest
from west.utils import is_version
from west.utils import sort_versions
from west.utils import until


def test_sort_versions():
    values = sort_versions(["1.0.1", "10.0", "2.0", "1.1", "1.0.3"])

    assert values == ["1.0.1", "1.0.3", "1.1", "2.0", "10.0"]


@pytest.mark.parametrize("value,expected", [("1.2", True), ("bananas", False)])
def test_is_version(value, expected):
    assert is_version(value) == expected


def test_until():
    values = list(until(range(300), 3))

    assert values == [0, 1, 2, 3]


def test_until_error():
    with pytest.raises(ValueError):
        list(until(range(5), 10))
