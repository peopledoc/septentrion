class SeptentrionException(Exception):
    pass


class NoDefaultConfiguration(SeptentrionException):
    pass


class NoSeptentrionSection(SeptentrionException):
    pass


class InvalidVersion(SeptentrionException):
    pass
