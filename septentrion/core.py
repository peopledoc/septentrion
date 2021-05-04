"""
This is where the migration plan is computed, by merging information
from the existing files (septentrion.files) and from the db (septentrion.db)
"""
import logging
from typing import Any, Dict, Iterable, Optional

from septentrion import configuration, db, exceptions, files, style, utils, versions

logger = logging.getLogger(__name__)


def initialize(**kwargs):
    settings = configuration.Settings(**kwargs)

    if settings.CREATE_TABLE:
        # All other commands will need the table to be created
        logger.info("Ensuring migration table exists")
        db.create_table(settings=settings)  # idempotent

    return settings


def get_applied_versions(
    settings: configuration.Settings,
) -> Iterable[versions.Version]:
    """
    Return the list of applied versions.
    Reuse django migration table.
    """
    applied_versions = set(db.get_applied_versions(settings=settings))

    known_versions = set(files.get_known_versions(settings=settings))

    return sorted(applied_versions & known_versions)


# TODO: Refactor: this should just work with version numbers, not sql_tpl and
# not force_version
def get_closest_version(
    settings: configuration.Settings,
    target_version: Optional[versions.Version],
    sql_tpl: str,
    existing_files: Iterable[str],
    force_version: Optional[versions.Version] = None,
) -> Optional[versions.Version]:
    """
    Get the version of a file (schema or fixtures) to use to init a DB.
    Take the closest to the target_version. Can be the same version, or older.
    """
    # get known versions
    known_versions = files.get_known_versions(settings=settings)
    # find target version

    if not target_version:
        previous_versions = known_versions
    else:
        try:
            previous_versions = list(utils.until(known_versions, target_version))
        except ValueError:
            raise ValueError(
                "settings.TARGET_VERSION is improperly configured: "
                "version {} not found.".format(target_version)
            )

    # should we set a version from settings ?
    if force_version:
        if force_version not in previous_versions:
            raise ValueError(
                "settings.TARGET_VERSION is improperly configured: "
                "settings.SCHEMA_VERSION is more recent."
            )

        file = sql_tpl.format(force_version.original_string)
        if file in existing_files:
            return force_version

        # not found
        return None

    for version in previous_versions[::-1]:
        schema_file = sql_tpl.format(version.original_string)
        if schema_file in existing_files:
            return version

    # not found
    return None


# TODO: refactor this and the function below
# TODO: also remove files.get_special_files, it's not really useful
def get_best_schema_version(settings: configuration.Settings) -> versions.Version:
    """
    Get the best candidate to init the DB.
    """
    schema_files = files.get_special_files(
        root=settings.MIGRATIONS_ROOT, folder="schemas"
    )
    version = get_closest_version(
        settings=settings,
        target_version=settings.TARGET_VERSION,
        sql_tpl=settings.SCHEMA_TEMPLATE,
        force_version=settings.SCHEMA_VERSION,
        existing_files=schema_files,
    )

    if version is None:
        raise exceptions.SeptentrionException("Cannot find a schema to init the DB.")
    return version


def get_fixtures_version(
    settings: configuration.Settings, target_version: Optional[versions.Version]
) -> versions.Version:
    """
    Get the closest fixtures to use to init a new DB
    to the current target version.
    """
    fixture_files = files.get_special_files(
        root=settings.MIGRATIONS_ROOT, folder="fixtures"
    )
    version = get_closest_version(
        settings=settings,
        target_version=target_version,
        existing_files=fixture_files,
        sql_tpl=settings.FIXTURES_TEMPLATE,
    )

    if version is None:
        raise exceptions.SeptentrionException("Cannot find fixtures to init the DB.")
    return version


def build_migration_plan(
    settings: configuration.Settings, from_version: versions.Version
) -> Iterable[Dict[str, Any]]:
    """
    Return the list of migrations by version,
    from the version used to init the DB to the current target version.
    """
    # get known versions
    known_versions = files.get_known_versions(settings=settings)
    target_version = settings.TARGET_VERSION

    # get all versions to apply
    if not target_version:
        versions_to_apply = known_versions
    else:
        try:
            versions_to_apply = list(utils.until(known_versions, target_version))
        except ValueError:
            raise ValueError(
                "settings.TARGET_VERSION is improperly configured: "
                "version {} not found.".format(target_version)
            )

    versions_to_apply = list(utils.since(versions_to_apply, from_version))

    # get plan for each version to apply
    for version in versions_to_apply:
        version_plan = []
        # get applied migrations
        applied_migrations = db.get_applied_migrations(
            settings=settings, version=version
        )
        # get migrations to apply
        migrations_to_apply = files.get_migrations_files_mapping(
            settings=settings, version=version
        )
        migs = list(migrations_to_apply)
        migs.sort()
        # build plan
        for mig in migs:
            applied = mig in applied_migrations
            path = migrations_to_apply[mig]
            contents = files.file_lines_generator(path)
            is_manual = files.is_manual_migration(
                migration_path=path, migration_contents=contents
            )
            version_plan.append((mig, applied, path, is_manual))
        yield {"version": version, "plan": version_plan}


def describe_migration_plan(
    settings: configuration.Settings, stylist: style.Stylist = style.noop_stylist
) -> None:

    if not db.is_schema_initialized(settings=settings):
        from_version = get_best_schema_version(settings=settings)
        with stylist.activate("title") as echo:
            echo("Schema file version is {}".format(from_version))
    else:
        _from_version = db.get_current_schema_version(settings=settings)
        assert _from_version  # mypy shenanigans
        from_version = _from_version
        with stylist.activate("title") as echo:
            echo("Current version is {}".format(from_version))

    target_version = settings.TARGET_VERSION

    with stylist.activate("title") as echo:
        echo("Migrations will start from {}".format(from_version))

    with stylist.activate("title") as echo:
        echo(f"Target version is {target_version or 'latest'}")

    for plan in build_migration_plan(settings=settings, from_version=from_version):
        version = plan["version"]
        migrations = plan["plan"]

        with stylist.activate("title") as echo:
            echo("Version {}".format(version))

        for migration_elem in migrations:

            name, applied, path, is_manual = migration_elem
            stylist.draw_checkbox(name, checked=applied)
            stylist.echo()
