from septentrion import exceptions


class Version:
    def __init__(self, version_string: str):
        try:
            assert version_string
            self._version = tuple(int(e) for e in version_string.split("."))
        except (AssertionError, ValueError) as exc:
            raise exceptions.InvalidVersion(str(exc)) from exc

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._version < other._version
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Version):
            return self._version == other._version
        raise NotImplementedError

    def __repr__(self) -> str:
        version_string = ".".join(str(n) for n in self._version)
        return f'{self.__class__.__name__}("{version_string}")'
