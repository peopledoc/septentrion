"""
This is where the migration plan is computed, by merging information
from the existing files (west.files) and from the db (west.db)
"""

import io

from west import db
from west import exceptions
from west import files
from west import utils
from west.settings import settings


def get_applied_versions():
    """
    Return the list of applied versions.
    Reuse django migration table.
    """
    applied_versions = set(db.get_applied_versions())

    known_versions = set(files.get_known_versions())

    return utils.sort_versions(applied_versions & known_versions)


def get_closest_version(target_version, sql_tpl, existing_files,
                        force_version=None):
    """
    Get the version of a file (schema or fixtures) to use to init a DB.
    Take the closest to the target_version. Can be the same version, or older.
    """
    # get known versions
    known_versions = files.get_known_versions()
    # find target version

    try:
        previous_versions = list(utils.until(known_versions, target_version))
    except ValueError:
        raise ValueError(
            'settings.TARGET_VERSION is improperly configured: '
            'version {} not found.'.format(
                settings.TARGET_VERSION))

    # should we set a version from settings ?
    if force_version:
        if force_version not in previous_versions:
            raise ValueError(
                'settings.TARGET_VERSION is improperly configured: '
                'settings.SCHEMA_VERSION is more recent.')

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


def get_schema_version():
    """
    Get the version to use to init a new DB to the current target version.
    """
    version = get_closest_version(
        target_version=settings.TARGET_VERSION,
        sql_tpl=settings.SCHEMA_TEMPLATE,
        existing_files=files.get_known_schemas(),
        force_version=settings.SCHEMA_VERSION)

    if version is None:
        raise exceptions.WestException('Can not find a schema to init the DB.')
    return version


def get_fixtures_version(target_version):
    """
    Get the closest fixtures to use to init a new DB
    to the current target version.
    """
    version = get_closest_version(
        target_version=target_version,
        existing_files=files.get_known_fixtures(),
        sql_tpl=settings.FIXTURES_TEMPLATE)

    if version is None:
        raise exceptions.WestException('Can not find fixtures to init the DB.')
    return version


def is_manual_migration(file_handler):
    if '/manual/' in file_handler.name:
        return True

    if not file_handler.name.endswith('dml.sql'):
        return False

    for line in file_handler:
        if '--meta-psql:' in line:
            file_handler.seek(0)
            return True

    file_handler.seek(0)
    return False


def build_migration_plan():
    """
    Return the list of migrations by version,
    from the version used to init the DB to the current target version.
    """
    # get current version
    current_version = db.get_schema_version()
    if current_version is None:
        # schema not inited
        return None
    # get known versions
    known_versions = files.get_known_versions()
    # get applied versions
    applied_versions = get_applied_versions()

    migration_plan = {
        'current_version': current_version,
        'init_version': None,
        'plans': [],
    }

    first_version_index = known_versions.index(applied_versions[0])
    init_version = known_versions[first_version_index - 1]

    migration_plan['init_version'] = init_version

    # get all versions to apply
    try:
        versions_to_apply = list(
            utils.until(known_versions, settings.TARGET_VERSION))
    except ValueError:
        raise ValueError(
            'settings.TARGET_VERSION is improperly configured: '
            'version {} not found.'.format(
                settings.TARGET_VERSION))

    # get plan for each version to apply
    for version in versions_to_apply:
        version_plan = []
        # get applied migrations
        applied_migrations = db.get_applied_migrations(version)
        # get migrations to apply
        migrations_to_apply = files.get_migrations_files_mapping(version)
        migs = list(migrations_to_apply.keys())
        migs.sort()
        # build plan
        for mig in migs:
            applied = mig in applied_migrations
            path = migrations_to_apply[mig]
            with io.open(path, 'r', encoding='utf8') as f:
                is_manual = is_manual_migration(f)
            version_plan.append((mig, applied, path, is_manual))
        migration_plan['plans'].append({
            'version': version,
            'plan': version_plan
        })

    return migration_plan
