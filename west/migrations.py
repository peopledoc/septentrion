import io
import os
from distutils.version import StrictVersion
from importlib import import_module

from west import db


class DBException(Exception):
    pass


def is_version(vstring):
    try:
        StrictVersion(vstring)
    except ValueError:
        return False
    return True


def list_dirs(root):
    return [d for d in os.listdir(root)
            if os.path.isdir(os.path.join(root, d))]


def list_files(root):
    return [d for d in os.listdir(root)
            if os.path.isfile(os.path.join(root, d))]


def get_known_versions(settings):
    """
    Return the list of the known versions defined in migration repository,
    ordered.
    Ignore symlinks.
    """
    # get all subfolders
    try:
        dirs = list_dirs(settings.MIGRATIONS_ROOT)
    except OSError:
        raise ValueError(
            'settings.MIGRATIONS_ROOT is improperly configured.')

    # exclude symlinks and some folders (like schemas, fixtures, etc)
    versions = [
        d for d in dirs
        if not os.path.islink(os.path.join(settings.MIGRATIONS_ROOT, d))
        and is_version(d)]

    # sort versions
    versions.sort(key=StrictVersion)
    return versions


def get_applied_versions(settings):
    """
    Return the list of applied versions.
    Reuse django migration table.
    """
    applied_versions = {migration['version'] for migration in db.get_applied_migrations(settings)}

    known_versions = set(get_known_versions(settings))

    return sorted(applied_versions & known_versions, key=StrictVersion)


def get_migrations_to_apply(settings, version):
    """
    Return an dict containing the list of migrations to apply for
    the given version.
    Key: name of the migration.
    Value: path of the migration.
    """
    def filter_migrations(files):
        return [
            f for f in files
            if f.endswith('ddl.sql') or f.endswith('dml.sql')]

    version_root = os.path.join(settings.MIGRATIONS_ROOT, version)
    migrations = {}

    # list auto migrations
    try:
        files = list_files(version_root)
    except OSError:
        raise DBException('No sql folder found for version {}.'.format(
            version))
    # filter files (keep *ddl.sql and *dml.sql)
    auto_migrations = filter_migrations(files)
    # store migrations
    for mig in auto_migrations:
        migrations[mig] = os.path.join(version_root, mig)

    # list manual migrations
    manual_root = os.path.join(version_root, 'manual')
    try:
        files = list_files(manual_root)
    except OSError:
        files = []
    # filter files (keep *ddl.sql and *dml.sql)
    auto_migrations = filter_migrations(files)
    # store migrations
    for mig in auto_migrations:
        migrations[mig] = os.path.join(manual_root, mig)

    return migrations


def get_closest_version(settings, target_version, sql_tpl, force_version=None):
    """
    Get the version of a file (schema or fixtures) to use to init a DB.
    Take the closest to the target_version. Can be the same version, or older.
    """
    # get known versions
    known_versions = get_known_versions(settings)
    # find target version
    try:
        target_version_index = known_versions.index(target_version)
    except ValueError:
        raise ValueError(
            'settings.TARGET_VERSION is improperly configured: '
            'version {} not found.'.format(
                settings.TARGET_VERSION))

    # should we set a version from settings ?
    if force_version:
        if force_version not in known_versions[:target_version_index+1]:
            raise ValueError(
                'settings.TARGET_VERSION is improperly configured: '
                'settings.SCHEMA_VERSION is more recent.')

        path = sql_tpl.format(force_version)
        if os.path.exists(path):
            return force_version

        # not found
        return None

    for version in known_versions[:target_version_index + 1: -1]:
        schema_path = sql_tpl.format(version)
        if os.path.exists(schema_path):
            return version 


def get_schema_version(settings):
    """
    Get the version to use to init a new DB to the current target version.
    """
    version = get_closest_version(
        settings=settings,
        target_version=settings.TARGET_VERSION,
        sql_tpl=os.path.join(
            settings.MIGRATIONS_ROOT,
            'schemas',
            settings.SCHEMA_TPL
        ),
        force_version=getattr(settings, 'SCHEMA_VERSION', None))

    if version is None:
        raise DBException('Can not find a schema to init the DB.')
    return version


def get_fixtures_version(settings, target_version):
    """
    Get the closest fixtures to use to init a new DB
    to the current target version.
    """
    version = get_closest_version(
        settings=settings,
        target_version=target_version,
        sql_tpl=os.path.join(
            settings.MIGRATIONS_ROOT,
            'fixtures',
            settings.FIXTURES_TPL))

    if version is None:
        raise DBException('Can not find fixtures to init the DB.')
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


def build_migration_plan(settings):
    """
    Return the list of migrations by version,
    from the version used to init the DB to the current target version.
    """
    # get current version
    current_version = db.get_schema_version(settings)
    if current_version is None:
        # schema not inited
        return None
    # get known versions
    known_versions = get_known_versions(settings)
    # get applied versions
    applied_versions = get_applied_versions(settings)

    migration_plan = {
        'current_version': current_version,
        'init_version': None,
        'plans': [],
    }
    # --------------------------------------------------------------------------------------------------------
    # --------------  Refactoring was stopped here
    first_version_index = known_versions.index(applied_versions[0])
    init_version = known_versions[first_version_index - 1]
    migration_plan['init_version'] = init_version

    # get all versions to apply
    try:
        target_version_index = known_versions.index(
            settings.TARGET_VERSION)
    except ValueError:
        raise ValueError(
            'settings.TARGET_VERSION is improperly configured: '
            'version {} not found.'.format(
                settings.TARGET_VERSION))
    versions_to_apply = known_versions[
        first_version_index:target_version_index + 1]

    # get plan for each version to apply
    for version in versions_to_apply:
        version_plan = []
        # get applied migrations
        applied_migrations = get_applied_migrations(version)
        # get migrations to apply
        migrations_to_apply = get_migrations_to_apply(version)
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
