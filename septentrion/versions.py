import dataclasses

from septentrion import exceptions


@dataclasses.dataclass(order=True, unsafe_hash=True, frozen=True)
class Version:

    version_tuple: tuple = dataclasses.field(compare=True)
    original_string: str = dataclasses.field(compare=False)

    @classmethod
    def from_string(cls, version_string: str) -> "Version":
        try:
            assert version_string
            version_tuple = tuple(int(e) for e in version_string.split("."))
        except (AssertionError, ValueError) as exc:
            raise exceptions.InvalidVersion(str(exc)) from exc
        return cls(version_tuple=version_tuple, original_string=version_string)

    def __str__(self):
        return self.original_string
