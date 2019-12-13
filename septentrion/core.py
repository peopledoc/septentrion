"""
This is where the migration plan is computed, by merging information
from the existing files (septentrion.files) and from the db (septentrion.db)
"""

import os
from typing import Any, Dict, Iterable, Optional

from septentrion import configuration, db, exceptions, files, style, utils


def get_applied_versions(settings: configuration.Settings) -> Iterable[str]:
    """
    Return the list of applied versions.
    Reuse django migration table.
    """
    applied_versions = set(db.get_applied_versions(settings=settings))

    known_versions = set(files.get_known_versions(settings=settings))

    return utils.sort_versions(applied_versions & known_versions)


def get_closest_version(
    settings: configuration.Settings,
    target_version: str,
    sql_tpl: str,
    existing_files: Iterable[str],
    force_version: Optional[str] = None,
):
    """
    Get the version of a file (schema or fixtures) to use to init a DB.
    Take the closest to the target_version. Can be the same version, or older.
    """
    # get known versions
    known_versions = files.get_known_versions(settings=settings)
    # find target version

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

        file = sql_tpl.format(force_version)
        if file in existing_files:
            return force_version

        # not found
        return None

    for version in previous_versions[::-1]:
        schema_file = sql_tpl.format(version)
        if schema_file in existing_files:
            return version

    # not found
    return None


def get_best_schema_version(settings: configuration.Settings) -> str:
    """
    Get the best candidate to init the DB.
    """
    version = get_closest_version(
        settings=settings,
        target_version=settings.TARGET_VERSION,
        sql_tpl=settings.SCHEMA_TEMPLATE,
        existing_files=files.get_known_schemas(settings=settings),
        force_version=settings.SCHEMA_VERSION,
    )

    if version is None:
        raise exceptions.SeptentrionException("Cannot find a schema to init the DB.")
    return version


def get_fixtures_version(settings: configuration.Settings, target_version: str) -> str:
    """
    Get the closest fixtures to use to init a new DB
    to the current target version.
    """
    version = get_closest_version(
        settings=settings,
        target_version=target_version,
        existing_files=files.get_known_fixtures(settings=settings),
        sql_tpl=settings.FIXTURES_TEMPLATE,
    )

    if version is None:
        raise exceptions.SeptentrionException("Cannot find fixtures to init the DB.")
    return version
