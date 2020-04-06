from septentrion import metadata as _metadata_module
from septentrion.lib import (
    build_migration_plan,
    fake,
    is_schema_initialized,
    migrate,
    show_migrations,
)

__all__ = [
    "build_migration_plan",
    "fake",
    "is_schema_initialized",
    "migrate",
    "show_migrations",
]

_metadata = _metadata_module.extract_metadata("septentrion")
__author__ = _metadata["author"]
__author_email__ = _metadata["email"]
__license__ = _metadata["license"]
__url__ = _metadata["url"]
__version__ = _metadata["version"]
