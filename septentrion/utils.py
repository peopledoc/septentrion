"""
All functions in here should be easily unit testable
"""

from distutils.version import StrictVersion


def sort_versions(iterable):
    """
    Sorts an iterable of strings by increasing
    equivalent version number
    >>> sort_versions(["1.0.1", "2.0", "1.0.3"])
    ["1.0.1", "1.0.3", "2.0"]
    """
    return sorted(iterable, key=StrictVersion)


def is_version(vstring):
    """
    Returns True if vstring is a valid version descriptor
    >>> is_version("1.2")
    True
    >>> is_version("bananas")
    False
    """
    try:
        StrictVersion(vstring)
    except ValueError:
        return False
    return True


def until(iterable, value):
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
