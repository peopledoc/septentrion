"""
Interact with the migration files.
"""

import io
import os
from distutils.version import StrictVersion

from septentrion import utils
from septentrion.settings import settings


def list_dirs(root):
    return [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]


def list_files(root):
    return [d for d in os.listdir(root) if os.path.isfile(os.path.join(root, d))]


def get_known_versions():
    """
    Return the list of the known versions defined in migration repository,
    ordered.
    Ignore symlinks.
    """
    # get all subfolders
    try:
        dirs = list_dirs(settings.MIGRATIONS_ROOT)
    except OSError:
        raise ValueError("settings.MIGRATIONS_ROOT is improperly configured.")

    # exclude symlinks and some folders (like schemas, fixtures, etc)
    versions = [
        d
        for d in dirs
        if not os.path.islink(os.path.join(settings.MIGRATIONS_ROOT, d))
        and utils.is_version(d)
    ]

    # sort versions
    versions.sort(key=StrictVersion)
    return versions


def is_manual_migration(migration_path):

    if "/manual/" in migration_path:
        return True

    if not migration_path.endswith("dml.sql"):
        return False

    with io.open(migration_path, "r", encoding="utf8") as f:
        for line in f:
            if "--meta-psql:" in line:
                return True

    return False


def get_known_schemas():
    return os.listdir(os.path.join(settings.MIGRATIONS_ROOT, "schemas"))


def get_known_fixtures():
    try:
        return os.listdir(os.path.join(settings.MIGRATIONS_ROOT, "fixtures"))
    except FileNotFoundError:
        return []


def get_migrations_files_mapping(version):
    """
    Return an dict containing the list of migrations for
    the given version.
    Key: name of the migration.
    Value: path to the migration file.
    """

    def filter_migrations(files):
        return [f for f in files if f.endswith("ddl.sql") or f.endswith("dml.sql")]

    version_root = os.path.join(settings.MIGRATIONS_ROOT, version)
    migrations = {}

    # list auto migrations
    try:
        files = list_files(version_root)
    except OSError:
        raise ValueError("No sql folder found for version {}.".format(version))
    # filter files (keep *ddl.sql and *dml.sql)
    auto_migrations = filter_migrations(files)
    # store migrations
    for mig in auto_migrations:
        migrations[mig] = os.path.join(version_root, mig)

    # list manual migrations
    manual_root = os.path.join(version_root, "manual")
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
