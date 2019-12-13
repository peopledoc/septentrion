"""
All functions in here should be easily unit testable
"""
from typing import Iterable, Optional, Tuple, TypeVar

from septentrion import exceptions


class Version:
    def __init__(self, version: str):
        try:
            assert version
            version_tuple = tuple(int(e) for e in version.split("."))
        except (AssertionError, ValueError) as exc:
            raise exceptions.InvalidVersion(str(exc)) from exc

        self._version = version_tuple


def is_version(vstring: str) -> bool:
    """
    Returns True if vstring is a valid version descriptor
    >>> is_version("1.2")
    True
    >>> is_version("bananas")
    False
    """
    try:
        Version(vstring)
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
