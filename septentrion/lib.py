import logging
from typing import Iterable

from septentrion import core, db, files, migration, style, versions

logger = logging.getLogger(__name__)


def initialize(settings_kwargs):
    quiet = settings_kwargs.pop("quiet", False)
    stylist = style.noop_stylist if quiet else style.stylist

    settings = core.initialize(**settings_kwargs)
    return {"settings": settings, "stylist": stylist}


def show_migrations(**settings_kwargs):
    lib_kwargs = initialize(settings_kwargs)
    core.describe_migration_plan(**lib_kwargs)


def migrate(**settings_kwargs):
    lib_kwargs = initialize(settings_kwargs)
    migration.migrate(**lib_kwargs)


def is_schema_initialized(**settings_kwargs):
    lib_kwargs = initialize(settings_kwargs)
    return db.is_schema_initialized(settings=lib_kwargs["settings"])


def build_migration_plan(**settings_kwargs):
    lib_kwargs = initialize(settings_kwargs)
    schema_version = core.get_best_schema_version(settings=lib_kwargs["settings"])
    return core.build_migration_plan(
        settings=lib_kwargs["settings"], schema_version=schema_version
    )


def fake(version: str, **settings_kwargs):
    lib_kwargs = initialize(settings_kwargs)
    fake_version = versions.Version.from_string(version)
    migration.create_fake_entries(version=fake_version, **lib_kwargs)


def load_fixtures(version: str, **settings_kwargs) -> None:
    lib_kwargs = initialize(settings_kwargs)
    init_version = versions.Version.from_string(version)
    migration.load_fixtures(init_version=init_version, **lib_kwargs)


def get_known_versions(**settings_kwargs) -> Iterable[str]:
    lib_kwargs = initialize(settings_kwargs)
    known_versions = files.get_known_versions(settings=lib_kwargs["settings"])
    return [version.original_string for version in known_versions]
