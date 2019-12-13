"""
All functions in here should be easily unit testable
"""

from typing import Iterable, TypeVar

from septentrion import exceptions, versions


def sort_versions(iterable: Iterable[str]) -> Iterable[str]:
    """
    Sorts an iterable of strings by increasing
    equivalent version number
    >>> sort_versions(["1.0.1", "2.0", "1.0.3"])
    ["1.0.1", "1.0.3", "2.0"]
    """
    return sorted(iterable, key=versions.Version)


def get_max_version(iterable: Iterable[str]) -> str:
    """
    Returns the latest version in the input iterable
    >>> get_max_version(["1.3", "1.2"])
    "1.3"
    """
    return max(iterable, key=versions.Version)


def is_version(vstring: str) -> bool:
    """
    Returns True if vstring is a valid version descriptor
    >>> is_version("1.2")
    True
    >>> is_version("bananas")
    False
    """
    try:
        versions.Version(vstring)
    except exceptions.InvalidVersion:
        return False
    return True


T = TypeVar("T")


def until(iterable: Iterable[T], value: T) -> Iterable[T]:
    """
    Returns the values from iterable up until element is found
    >>> list(until(range(300), 3))
    [0, 1, 2, 3]
    """
    for element in iterable:
        yield element
        if element == value:
            break
    else:
        raise ValueError("{} not found".format(value))
