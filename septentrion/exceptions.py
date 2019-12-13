class SeptentrionException(Exception):
    pass


class NoDefaultConfiguration(SeptentrionException):
    pass


class NoSeptentrionSection(SeptentrionException):
    pass


class InvalidVersion(SeptentrionException, ValueError):
    pass


class FileError(SeptentrionException, OSError):
    pass
