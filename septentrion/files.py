"""
Interact with the migration files.
"""

import io
import pathlib
from typing import Iterable

from septentrion import configuration, utils, exceptions


def list_dirs(root: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    List dirs under root
    """
    try:
        return [d for d in root.iterdir() if d.is_dir()]
    except OSError as exc:
        raise exceptions.FileError from exc


def list_files(root: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    List files under root that are not symlinks
    """
    try:
        return [f for f in root.iterdir() if f.is_file() and not f.is_symlink()]
    except OSError as exc:
        raise exceptions.FileError from exc


def get_file_versions(migration_root: pathlib.Path) -> Iterable[utils.Version]:
    """
    Return the list of the folders in migration root for which the name is a valid
    version numbers. There are the migration version we know from the files.
    """
    # get all subfolders
    dirs = list_dirs(migration_root)

    # Keep only folder names that are valid version numbers
    versions = []
    for dir in dirs:
        try:
            versions.append(utils.Version(str(dir)))
        except exceptions.InvalidVersion:
            continue

    return sorted(versions)


def get_known_schemas(settings: configuration.Settings) -> Iterable[str]:
    return os.listdir(os.path.join(settings.MIGRATIONS_ROOT, "schemas"))


def get_known_fixtures(settings: configuration.Settings) -> Iterable[str]:
    try:
        return os.listdir(os.path.join(settings.MIGRATIONS_ROOT, "fixtures"))
    except FileNotFoundError:
        return []


def get_migrations_files_mapping(settings: configuration.Settings, version: str):
    """
    Return an dict containing the list of migrations for
    the given version.
    Key: name of the migration.
    Value: path to the migration file.
    """

    def filter_migrations(files: Iterable[str]) -> Iterable[str]:
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
