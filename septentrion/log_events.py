import enum


class LogEvent(enum.Enum):
    VERSION_START = "version_start"
    VERSION_END = "version_end"
    MIGRATION_START = "migration_start"
    MIGRATION_END = "migration_end"
