"""
All functions in here should be easily unit testable
"""

import itertools
from typing import Iterable, TypeVar

from septentrion import exceptions, versions


def is_version(vstring: str) -> bool:
    """
    Returns True if vstring is a valid version descriptor
    >>> is_version("1.2")
    True
    >>> is_version("bananas")
    False
    """
    try:
        versions.Version.from_string(vstring)
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


def since(iterable: Iterable[T], value: T) -> Iterable[T]:
    """
    Returns the values from iterable starting after the element is found
    >>> list(until(range(300), 297))
    [297, 298, 299]
    """
    yield from itertools.dropwhile((lambda x: x != value), iterable)
